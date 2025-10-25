(eval-when (:compile-toplevel :load-toplevel :execute) (ql:quickload '(:clack :woo :cffi :lack :alexandria :flexi-streams :log4cl :com.inuoe.jzon)))
(defpackage :itrivia (:use :cl) (:export :main))
(in-package :itrivia)

(cffi:define-foreign-library sqlite3 (:unix (:or "libsqlite3.so.0" "libsqlite3.so")))
(cffi:use-foreign-library sqlite3)
(cffi:defctype db-p :pointer)
(cffi:defcfun ("sqlite3_open" db-up) :int (filename :string) (ppdb (:pointer db-p)))
(cffi:defcfun ("sqlite3_close_v2" db-down) :int (db db-p))
(cffi:defcfun ("sqlite3_exec" ex) :int (db db-p) (sql :string) (callback :pointer) (arg :pointer) (errmsg :pointer))

(defvar *r* nil)

(cffi:defcallback %exec-callback :int
    ((arg :pointer) (ncols :int) (values (:pointer :string)) (colnames (:pointer :string)))
  (declare (ignore arg))
  (let ((row
          (loop for i below ncols
                append (list (intern (string-upcase (cffi:mem-aref colnames :string i))
                                     :keyword)
                             (or (cffi:mem-aref values :string i) "")))))
    (push row *r*))
  0)

(defun dbex (&rest vals)
  (cffi:with-foreign-object (pp 'db-p)
    (let ((rc (db-up "./itrivia.db" pp)))
      (if (plusp rc)
          (values nil rc)
          (let ((db (cffi:mem-ref pp 'db-p)))
            (unwind-protect
                 (let ((*r* nil))
                   (let ((rc2 (ex db (format nil "~{~a~}" vals)
				  (cffi:callback %exec-callback)
				  (cffi:null-pointer)
				  (cffi:null-pointer))))
                     (values (nreverse *r*) rc2)))
              (db-down db)))))))

(defun format-value (input-string)
  (with-output-to-string (s)
    (loop for char across input-string do
      (princ char s)
      (when (char= char #\')
	(princ char s)))))

(defparameter +cors-headers+ '(:access-control-allow-origin "*"
                               :access-control-allow-methods "GET, POST, PUT, DELETE, OPTIONS"
                               :access-control-allow-headers "Content-Type, User"
                               :access-control-max-age "86400") "CORS headers")
(defparameter +headers+ (append '(:content-type "text/plain; charset=utf-8") +cors-headers+) "Default response headers")
(defparameter +allowed-questions+ 3 "Any user can only answer this many questions")
(defparameter +unauthorized+ `(403 ,+headers+ ("Unauthorized")) "Unauthorized response")

(defun user-check (headers)
  (let ((res (dbex "SELECT * FROM users WHERE code = '" (gethash "user" headers) "'")))
    (if res (first res) nil)))

(defmacro http-enforce-for (name &rest clauses) `(unless (and ,@clauses t) (return-from ,name +unauthorized+)))
(defmacro getf-int (model field) `(or (parse-integer (or (getf ,model ,field) "0") :junk-allowed t) 0))

(defun single-trivia (query mult)
  (let* ((entity-count (+ 2 (random 98)))
         (base-answer (floor (* mult entity-count)))
         (deterrant (- (random 21) 10))) ; We can't have people winning, right?
    (list (format nil query entity-count) (+ base-answer deterrant))))

(defun generate-trivia ()
  (nth
   (random 8)
   (list
    (single-trivia "How many adult male Guira Cuckoos fit into ~r adult male Borneo Pygmy Elephants?" 27797)
    (single-trivia "How many seconds are in ~r years?" 31556926)
    (single-trivia "How many how many one dollar bills were printed on average in ~r seconds in 2024?" 64)
    (single-trivia "In any given ~r day period in 2016, how many people died from a scorpion?" 10)
    (single-trivia "If Pop Laurentiu held his world-record pace for ~r hours, how many pushups will he have done?" 3378)
    (single-trivia "How many cow tongues would it take to circle the moon ~r times at surface level?" 8550036)
    (single-trivia "In any given ~r millenium period, an average immortal American eats how many burgers?" 156000)
    (single-trivia "An iPhone 16 Pro Max consumes how many watts of power on average in a ~r hour period?" 3.45))))

(defun index (env)
  (declare (ignore env))
  `(200 ,(append '(:content-type "text/html; charset=utf-8") +cors-headers+)
	(,(with-open-file
	      (file-s #P"./public/index.html" :direction :input :if-does-not-exist nil)
	    (let ((s (make-string (file-length file-s))))
	      (read-sequence s file-s)
	      s)))))

(defun new (env)
  (declare (ignore env))
  `(200 ,+headers+ (,(progn (getf (car (dbex "INSERT INTO users DEFAULT VALUES RETURNING code")) :code)))))

(defun next (env)
  (destructuring-bind (&key headers &allow-other-keys) env
    (let* ((user-row (user-check headers))
	   (check
	     (http-enforce-for
	      next
	      user-row
	      (< (getf-int user-row :answers_given) +allowed-questions+)
	      (dbex "SELECT * FROM users WHERE id = " (getf-int user-row :id) " AND current_question_id IS NULL")))
	   (trivia (generate-trivia))
	   (trivia-id
	     (getf
	      (first
	       (dbex "INSERT INTO trivia (question, answer) VALUES ('" (first trivia) "', '" (second trivia) "') RETURNING id")) :id)))
      (declare (ignore check))

      (dbex "UPDATE users SET current_question_id = " trivia-id " WHERE id = " (getf user-row :id))
      `(200 ,+headers+ (,(first trivia))))))

(defun status (env)
  (destructuring-bind (&key headers &allow-other-keys) env
    (let* ((user-row (user-check headers))
	   (check (http-enforce-for status user-row))
	   (answers-given (getf-int user-row :answers_given))
	   (game-over (if (>= answers-given +allowed-questions+) "TRUE" "FALSE"))
	   (min-delta (getf-int user-row :min_guess_delta))
	   (trivias
	     (loop for trivia in (or (dbex
				      "SELECT * FROM users_trivia ut WHERE ut.user_id = "
				      (getf user-row :id) " ORDER BY ut.answer_order ASC") '())
		   for i from 1
		   collect (let
			       ((tr (make-hash-table)))
			     (setf (gethash 'correct tr) (string= "1" (getf trivia :correct)))
			     (setf (gethash 'delta tr) (getf-int trivia :guess_delta))
			     (setf (gethash 'index tr) i)
			     tr)))
	   (response (make-hash-table)))
      (declare (ignore check))

      (setf (gethash 'game_over response) (string= game-over "TRUE"))
      (setf (gethash 'min_guess_delta response) min-delta)
      (setf (gethash 'allowed_questions response) +allowed-questions+)
      (setf (gethash 'answers_given response) answers-given)
      (setf (gethash 'trivia_results response) (or trivias (make-array 0)))
      
      `(200 ,+headers+ (,(com.inuoe.jzon:stringify response))))))

(defun answer (env)
  (destructuring-bind (&key headers raw-body &allow-other-keys) env
    (let* ((user-row (user-check headers))
	   (check
	     (http-enforce-for
	      answer 
	      user-row
	      (< (getf-int user-row :answers_given) +allowed-questions+)
	      (not (dbex "SELECT * FROM users WHERE id = "(getf user-row :id)" AND current_question_id IS NULL"))
	      (not (dbex "SELECT * FROM users_trivia WHERE user_id = " (getf user-row :id)" AND trivia_id = " (getf user-row :current_question_id)))))
	   (byte-vector (alexandria:read-stream-content-into-byte-vector raw-body))
	   (body-string (format-value (flexi-streams:octets-to-string byte-vector :external-format :utf-8)))
	   (user-answer-int (or (parse-integer body-string :junk-allowed t) (return-from answer +unauthorized+)))
	   (db-answer-check
	     (dbex "SELECT CASE WHEN trivia.answer = '" body-string "' THEN TRUE ELSE FALSE END AS correct, trivia.answer "
		   "FROM trivia LEFT JOIN users on users.current_question_id = trivia.id WHERE users.id = " (getf user-row :id)))
	   (is-correct (and db-answer-check (string= "1" (getf (first db-answer-check) :correct))))
	   (correct-answer (when db-answer-check (getf-int (first db-answer-check) :answer)))
	   (difference (when (and correct-answer (not is-correct)) (abs (- user-answer-int correct-answer))))
	   (response (if is-correct "TRUE" (format nil "FALSE:~a:~a" correct-answer difference))))

      (declare (ignore check))

      (dbex "INSERT INTO users_trivia (answer_order, user_id, trivia_id, correct, guess_delta) VALUES ("
	    (getf (first (dbex "SELECT COUNT(*) AS count FROM users_trivia WHERE user_id = "
			(getf user-row :id))) :count) ", "
	    (getf user-row :id) ", "
	    (getf user-row :current_question_id) ", "
	    (if is-correct "TRUE" "FALSE") ", " 
	    (or difference 0) ")")

      (dbex "UPDATE USERS SET current_question_id = NULL WHERE id = " (getf user-row :id))
      
      `(200 ,+headers+ (,response)))))

(defparameter *app*
  (lambda (env)
    (destructuring-bind (&key path-info request-method &allow-other-keys)
	env
      ;; Handle OPTIONS preflight requests
      (if (eq request-method :options)
          `(200 ,+cors-headers+ (""))
          (cond
            ((string= path-info "/") (index env))
            ((string= path-info "/new") (new env))
            ((string= path-info "/next") (next env))
            ((string= path-info "/status") (status env))
            ((string= path-info "/answer") (answer env))
            (t '(404 nil ("Not Found"))))))))


(defun main ()
  (dbex "CREATE TABLE IF NOT EXISTS users ("
	"  id INTEGER PRIMARY KEY,"
	"  code TEXT NOT NULL UNIQUE ON CONFLICT ROLLBACK CHECK(LENGTH(code) > 15) DEFAULT (DATETIME() || LOWER(HEX(RANDOMBLOB(25)))),"
	"  correct_answers INTEGER NOT NULL DEFAULT 0 CHECK(0 <= correct_answers AND correct_answers <= 100),"
	"  answers_given INTEGER NOT NULL DEFAULT 0 CHECK(0 <= answers_given AND answers_given <= 3),"
	"  current_question_id INTEGER,"
	"  min_guess_delta INTEGER,"
	"  FOREIGN KEY (current_question_id) REFERENCES trivia (id)"
	")")

  (dbex "CREATE TABLE IF NOT EXISTS trivia ("
	"  id INTEGER PRIMARY KEY,"
	"  question TEXT NOT NULL CHECK(LENGTH(question) <= 255),"
	"  answer INTEGER NOT NULL DEFAULT 0"
	")")

  (dbex "CREATE TABLE IF NOT EXISTS users_trivia ("
	"  answer_order INTEGER NOT NULL,"
	"  user_id INTEGER NOT NULL,"
	"  trivia_id INTEGER NOT NULL,"
	"  correct BOOLEAN NOT NULL CHECK(correct in (0,1)),"
	"  guess_delta INTEGER NOT NULL DEFAULT 0,"
	"  FOREIGN KEY(user_id) REFERENCES users(id),"
	"  FOREIGN KEY(trivia_id) REFERENCES trivia(id),"
	"  PRIMARY KEY(user_id, trivia_id) ON CONFLICT IGNORE"
	")")

  (dbex "CREATE TRIGGER IF NOT EXISTS update_status "
	"AFTER INSERT ON users_trivia BEGIN "
	"  UPDATE users"
	"  SET correct_answers = ("
	"    SELECT COUNT(*)"
	"    FROM users_trivia utr"
	"    WHERE utr.user_id = users.id"
	"    AND utr.correct = TRUE"
	"  ), answers_given = ("
	"    SELECT COUNT(*)"
	"    FROM users_trivia utr2"
	"    WHERE utr2.user_id = users.id"
	"  ), min_guess_delta = ("
	"    SELECT MIN(guess_delta)"
	"    FROM users_trivia utr3"
	"    WHERE utr3.user_id = users.id"
	"  )"
	"  WHERE NEW.user_id = users.id;"
	"END")
  (defparameter *server*
    (clack:clackup
     (lack:builder
      (:static :path "/assets/" :root #P"./public/assets/")
      (:static :path "/wasm/" :root #P"./public/wasm/")
      *app*) 
     :server :woo 
     :port 6006 
     :address "0.0.0.0")))

(main)


package controllers

import javax.inject._
import play.api._
import play.api.mvc._
import play.api.data._
import play.api.data.Forms._
import play.api.i18n._
import java.security.SecureRandom
import java.io.{File, FileWriter, PrintWriter}
import scala.util.{Try, Success, Failure}
import scala.collection.mutable
import java.util.UUID

case class GameState(targetNumber: Int, attempts: Int, guesses: List[Int])

object GameStateStore {
  private val gameStates = mutable.Map[String, GameState]()
  private val random = new SecureRandom()
  
  def createGame(): (String, GameState) = {
    val sessionId = UUID.randomUUID().toString
    val targetNumber = generateNewNumber()
    val gameState = GameState(targetNumber, 0, List.empty)
    gameStates(sessionId) = gameState
    (sessionId, gameState)
  }
  
  def getGame(sessionId: String): Option[GameState] = {
    gameStates.get(sessionId)
  }
  
  def updateGame(sessionId: String, gameState: GameState): Unit = {
    gameStates(sessionId) = gameState
  }
  
  def removeGame(sessionId: String): Unit = {
    gameStates.remove(sessionId)
  }
  
  def generateNewNumber(): Int = {
    val i = random.nextInt()
    println("generating next int", i)
    i
  }
}

@Singleton
class GameController @Inject()(val controllerComponents: ControllerComponents, configuration: Configuration)(implicit messagesApi: MessagesApi) extends BaseController with I18nSupport {

  val guessForm = Form(
    "guess" -> number
  )

  private val isTestMode = configuration.getOptional[String]("test.mode").isDefined

  private def writeTargetNumberForTest(sessionId: String, targetNumber: Int): Unit = {
    if (isTestMode) {
      Try {
        val file = new File(s"/shared/target_${sessionId}.txt")
        val writer = new PrintWriter(new FileWriter(file, false))
        writer.println(targetNumber)
        writer.close()
      } match {
        case Success(_) => ()
        case Failure(e) => println(s"Failed to write target number: ${e.getMessage}")
      }
    }
  }


  def index() = Action { implicit request: Request[AnyContent] =>
    val (sessionId, gameState) = GameStateStore.createGame()
    writeTargetNumberForTest(sessionId, gameState.targetNumber)
    
    Ok(views.html.game(guessForm, gameState, None))
      .withSession("sessionId" -> sessionId)
  }

  def health() = Action { implicit request: Request[AnyContent] =>
    Ok("OK")
  }

  def guess() = Action { implicit request: Request[AnyContent] =>
    request.session.get("sessionId") match {
      case None => Redirect(routes.GameController.index())
      case Some(sessionId) =>
        GameStateStore.getGame(sessionId) match {
          case None => Redirect(routes.GameController.index())
          case Some(currentGameState) =>
            guessForm.bindFromRequest().fold(
              formWithErrors => {
                BadRequest(views.html.game(formWithErrors, currentGameState, Some("Invalid guess")))
                  .withSession("sessionId" -> sessionId)
              },
              userGuess => {
                val newAttempts = currentGameState.attempts + 1
                val newGuesses = userGuess :: currentGameState.guesses

                if (userGuess == currentGameState.targetNumber) {
                  writeScore(newGuesses, currentGameState.targetNumber)
                  GameStateStore.removeGame(sessionId)
                  val score = getScore(newGuesses, currentGameState.targetNumber)
                  Ok(views.html.game(guessForm, GameState(currentGameState.targetNumber, newAttempts, newGuesses), Some(s"Congratulations! You guessed correctly! Your score is: $score")))
                    .withNewSession
                } else if (newAttempts >= 2) {
                  writeScore(newGuesses, currentGameState.targetNumber)
                  val closestGuess = getClosestGuess(newGuesses, currentGameState.targetNumber)
                  val score = getScore(newGuesses, currentGameState.targetNumber)
                  val message = s"Game over! The number was ${currentGameState.targetNumber}. Your closest guess was $closestGuess. Your score is: $score"
                  GameStateStore.removeGame(sessionId)
                  Ok(views.html.game(guessForm, GameState(currentGameState.targetNumber, newAttempts, newGuesses), Some(message)))
                    .withNewSession
                } else {
                  val newTargetNumber = GameStateStore.generateNewNumber()
                  val hint = if (userGuess < currentGameState.targetNumber) "Too low!" else "Too high!"
                  val updatedGameState = GameState(newTargetNumber, newAttempts, newGuesses)
                  GameStateStore.updateGame(sessionId, updatedGameState)
                  writeTargetNumberForTest(sessionId, newTargetNumber)
                  Ok(views.html.game(guessForm, updatedGameState, Some(s"$hint The number was ${currentGameState.targetNumber}. Try again with a new number.")))
                    .withSession("sessionId" -> sessionId)
                }
              }
            )
        }
    }
  }

  private def getClosestGuess(guesses: List[Int], target: Int): Int = {
    guesses.minBy(guess => math.abs(guess - target))
  }

  private def getScore(guesses: List[Int], target: Int): Int = {
    if (guesses.isEmpty) 0
    else {
      val closestGuess = getClosestGuess(guesses, target)
      math.abs(closestGuess - target)
    }
  }

  private def writeScore(guesses: List[Int], targetNumber: Int): Unit = {
    if (guesses.nonEmpty) {
      val closestGuess = getClosestGuess(guesses, targetNumber)
      val difference = math.abs(closestGuess - targetNumber)
      
      Try {
        val file = new File("/shared/oracle_score.txt")
        val writer = new PrintWriter(new FileWriter(file, true))
        writer.println(s"$difference")
        writer.close()
      } match {
        case Success(_) => ()
        case Failure(e) => println(s"Failed to write score: ${e.getMessage}")
      }
    }
  }
}

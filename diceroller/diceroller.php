<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Carnival d20 Roller</title>
    <style>
        @font-face {
            font-family: "saintcarnsolas";
            src: url("https://sc-25.cdn.cbj-x.com/saintcarnsolas.woff") format("woff"),
                url("https://sc-25.cdn.cbj-x.com/saintcarnsolas.woff2") format("woff2");
            font-weight: normal;
            font-style: normal;
        }

        @font-face {
            font-family: "a dripping marker";
            src: url("https://sc-25.cdn.cbj-x.com/adrip1.woff") format("woff"),
                url("https://sc-25.cdn.cbj-x.com/adrip1.woff2") format("woff2");
            font-weight: normal;
            font-style: normal;
        }

        @font-face {
            font-family: "SDDystopian";
            src: url("https://sc-25.cdn.cbj-x.com/SDDystopian.woff") format("woff"),
                url("https://sc-25.cdn.cbj-x.com/SDDystopian.woff2") format("woff2");
            font-weight: normal;
            font-style: normal;
        }

        html,
        body {
            --three-dee-dice-size: 40px;
            --three-dee-dice-hue: 210;
            --three-dee-dice-hue-correct: 150;
            --three-dee-dice-sat: 55%;
            --three-dee-dice-light: 85%;
            --three-dee-dice-light-correct: 55%;
            --three-dee-dice-face1: hsl(var(--three-dee-dice-hue) var(--three-dee-dice-sat) calc(var(--three-dee-dice-light) + 6%));
            --three-dee-dice-face2: hsl(var(--three-dee-dice-hue) var(--three-dee-dice-sat) calc(var(--three-dee-dice-light) - 6%));
            --three-dee-dice-approved1: hsl(var(--three-dee-dice-hue-correct) var(--three-dee-dice-sat) calc(var(--three-dee-dice-light-correct) + 6%));
            --three-dee-dice-approved2: hsl(var(--three-dee-dice-hue-correct) var(--three-dee-dice-sat) calc(var(--three-dee-dice-light-correct) - 6%));
            --three-dee-dice-edge-dark: rgba(0, 0, 0, .01);
            --three-dee-dice-spec: hsla(0 0% 100% / .6);

            --game-bg-color: #171717;
            --sc-orange: #e05a00;
            --sc-red: #693126;
            --blue: #005ae0;
            --red: #e02200;
            --yellow: #fcf300;
            --off-white: #e4ffe4;
            --terminal-green: #007e3c;
            --correct: rgb(83, 141, 78);
            --present: rgb(181, 159, 59);
            --absent: rgb(58, 58, 60);
            height: 100%;
            padding: 0;
            margin: 0;
            transition: transform 0.5s;

        }

        .carnival {
            background-image: url("https://sc-25.cdn.cbj-x.com/backdrop.png");
            background-repeat: no-repeat;
            background-position: center center;
            background-size: cover;
            width: 100%;
            height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 0;
            margin: 0;

            /* Unreasonable styling requests */
            @media only screen and (max-width: 450px) {
                * {
                    scale: 90%;
                }
            }

            @media only screen and (max-width: 350px) {
                * {
                    scale: 80%;
                }
            }

            @media only screen and (max-width: 250px) {
                * {
                    scale: 70%;
                }
            }
        }

        main {
            margin: 50px;
            padding: 1.2rem;
            background-image: url("https://sc-25.cdn.cbj-x.com/rust-backdrop.png");
            background-repeat: no-repeat;
            background-position: center center;
            border-radius: 15px;
            box-shadow: 10px 10px 20px rgba(0, 0, 0, 0.1);
            width: 80%;
            max-width: fit-content;
        }

        header {
            background-image: url("https://sc-25.cdn.cbj-x.com/sign-black.png");
            background-repeat: no-repeat;
            background-position: center center;
            background-size: contain;
            margin-bottom: -7rem;
            z-index: 10;
            padding: 2rem;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            rotate: 5deg;

            h1 {
                text-align: center;
                font-family: "saintcarnsolas", monospace;
                font-size: 1.7em;
                text-shadow: 3px 3px #ff5733;
                color: white;

                >span {
                    font-size: .75em;
                }
            }

            p {
                position: absolute;
                font-family: "a dripping marker", Arial, sans-serif;
                font-size: 2em;
                color: var(--off-white);
                letter-spacing: 5px;
                rotate: -5deg;
                margin: 1px;
                right: 50%;
                translate: 50%;
                bottom: 0;
            }
        }

        .game {
            min-width: 400px;
            min-height: 450px;
            border: 20px solid var(--game-bg-color);
            border-image: url("https://sc-25.cdn.cbj-x.com/nuts-n-lights-border.png") 31% fill / 20px / 15px space;
            background: radial-gradient(circle, #ffecb3, #ff9800);
            padding: 0 2rem;
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            color: white;

            * {
                font-family: "saintcarnsolas", monospace;
            }
        }

        .hidden {
            display: none;
        }

        .three-dee-button {
            background: #fff;
            border: 2px solid #888;
            font-size: 18px;
            cursor: pointer;
            border-radius: 10px;
            outline: none;
            margin-top: 1rem;
            padding: 0;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.15), 5px 14px 20px rgba(0, 0, 0, 0.15);
            transition: all 0.1s ease-in-out;

            &#submit {
                margin-top: 200px;
                background: var(--sc-orange);
                border: 2px solid #702d00;

                .three-dee-button__content {
                    box-shadow: inset 0 -6px #702d00, 0 -2px var(--sc-orange);
                }
            }

        }

        .three-dee-button__content {
            display: block;
            padding: 12px 40px;
            border-radius: 8px;
            transition: all 0.1s ease-in-out;
        }

        .three-dee-button__text {
            color: var(--off-white);
            display: block;
            transform: translate3d(0, -4px, 0);
            transition: all 0.1s ease-in-out;
            font-size: 1.2em;
        }

        .three-dee-button:active {
            box-shadow: none;
        }

        .three-dee-button:active .three-dee-button__content {
            box-shadow: none;
        }

        .three-dee-button:active .three-dee-button__text {
            transform: translate3d(0, 0, 0);
        }

        form {
            margin: 20px auto;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        input {
            padding: 10px;
            font-size: 1.2em;
            border: 2px solid #ff5733;
            border-radius: 10px;
            width: 300px;
            text-align: center;
        }

        .dice-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 25px;
            margin-top: 20px;
        }

        .dice-row {
            display: flex;
            justify-content: center;
            gap: 25px;
        }


        #rolling {
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
            background-image: url("https://sc-25.cdn.cbj-x.com/red-button.png");
            background-repeat: no-repeat;
            background-position: center center;
            background-size: cover;
            background-blend-mode: hue;
            opacity: 90%;
            width: 200px;
            height: 85px;
            color: white;
            margin-top: 40px;
            margin-bottom: -35px;
            font-weight: lighter;
        }

        @keyframes roll-diagonal {
            0% {
                transform: rotateX(0) rotateY(0) rotateZ(0);
            }

            15% {
                transform: rotateX(180deg) rotateY(90deg) rotateZ(20deg);
            }

            35% {
                transform: rotateX(360deg) rotateY(180deg) rotateZ(60deg);
            }

            60% {
                transform: rotateX(540deg) rotateY(270deg) rotateZ(100deg);
            }

            80% {
                transform: rotateX(720deg) rotateY(360deg) rotateZ(140deg);
            }

            100% {
                transform: rotateX(10deg) rotateY(10deg) rotateZ(10deg);
            }
        }

        .three-dee-dice {
            color: black;
            --three-dee-dice-half: calc(var(--three-dee-dice-size) / 2);
            position: relative;
            width: var(--three-dee-dice-size);
            height: var(--three-dee-dice-size);
            transform-style: preserve-3d;
            transform: rotateX(10deg) rotateY(10deg) rotateZ(10deg);

            &,
            & * {
                box-sizing: border-box;
            }

            &.green .three-dee-dice-face {
                background:
                    radial-gradient(160% 160% at 20% 14%, var(--three-dee-dice-spec) 0 8%, transparent 35%),
                    linear-gradient(145deg, var(--three-dee-dice-approved1), var(--three-dee-dice-approved2));
            }

            &.rolling {
                animation: roll-diagonal calc(3.2s - (var(--i) * .1s)) cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
                animation-delay: calc(var(--i) * .1s);
            }
        }

        .three-dee-dice:hover {
            animation-play-state: paused;
            background:
                radial-gradient(160% 160% at 20% 14%, var(--three-dee-dice-spec) 0 8%, transparent 35%),
                linear-gradient(145deg, var(--three-dee-dice-face1), var(--three-dee-dice-face2));
        }

        .three-dee-dice-face {
            font-family: "SDDystopian", monospace;
            font-size: 1.7em;
            padding: 5px 0;
            text-align: center;
            border: 5px solid var(--game-bg-color);
            border-image-source: url("https://sc-25.cdn.cbj-x.com/metal_border.png");
            border-image-slice: 10%;
            border-image-outset: 2px;
            background-size: 900%;
            background-position: center;
            background-repeat: no-repeat;
            position: absolute;
            inset: 0;
            width: var(--three-dee-dice-size);
            height: var(--three-dee-dice-size);
            background:
                radial-gradient(160% 160% at 20% 14%, var(--three-dee-dice-spec) 0 8%, transparent 35%),
                linear-gradient(145deg, var(--three-dee-dice-face1), var(--three-dee-dice-face2));
        }

        .three-dee-dice-face::after {
            content: "";
            position: absolute;
            inset: 0;
            box-shadow:
                inset 0 0 0 1px rgba(255, 255, 255, .05),
                inset 0 0 0 2px rgba(0, 0, 0, .15);
            pointer-events: none;
        }

        .three-dee-dice-front {
            transform: translateZ(var(--three-dee-dice-half));
        }

        .three-dee-dice-back {
            transform: rotateY(180deg) translateZ(var(--three-dee-dice-half));
        }

        .three-dee-dice-right {
            transform: rotateY(90deg) translateZ(var(--three-dee-dice-half));
        }

        .three-dee-dice-left {
            transform: rotateY(-90deg) translateZ(var(--three-dee-dice-half));
        }

        .three-dee-dice-top {
            transform: rotateX(90deg) translateZ(var(--three-dee-dice-half));
        }

        .three-dee-dice-bottom {
            transform: rotateX(-90deg) translateZ(var(--three-dee-dice-half));
        }

        .three-dee-dice-right {
            filter: brightness(.95);
        }

        .three-dee-dice-left {
            filter: brightness(.9);
        }

        .three-dee-dice-top {
            filter: brightness(1.05) contrast(1.02);
        }

        .three-dee-dice-bottom {
            filter: brightness(.85);
        }
    </style>
</head>

<body>
    <div class="carnival">
        <header>
            <h1>Carnival<br><span>🎪 d20 Roller 🎲</span></h1>
            <p>gambull</p>
        </header>
        <main>
            <div class="game">
                <form method="POST" onsubmit="setTimestamp()" id="form">
                    <input type="hidden" name="input_string" id="timestampInput">
                    <button name="submit" type="submit" class="three-dee-button" id="submit" role="button">
                        <span class="three-dee-button__content">
                            <span class="three-dee-button__text text">
                                Roll the Dice! 🎲
                            </span>
                        </span>
                    </button>
                </form>

                <?php
                use Random\RandomException;

                function base_convert_arbitrary($numStr, $toBase)
                {
                    $digits = '0123456789ABCDEFGHIJ';
                    $result = '';

                    while (bccomp($numStr, '0') > 0) {
                        $remainder = bcmod($numStr, $toBase);
                        $result = $digits[intval($remainder)] . $result;
                        $numStr = bcdiv($numStr, $toBase, 0);
                    }

                    return str_pad($result, 30, "0", STR_PAD_LEFT) ?: '0';
                }

                function md5_to_base20($input)
                {
                    $md5Hash = md5($input);
                    $decimalStr = '';
                    // Convert hex to decimal using BCMath
                    $length = strlen($md5Hash);
                    $power = '1';
                    for ($i = $length - 1; $i >= 0; $i--) {
                        $digit = hexdec($md5Hash[$i]);
                        $decimalStr = bcadd($decimalStr, bcmul($digit, $power));
                        $power = bcmul($power, '16');
                    }
                    return base_convert_arbitrary($decimalStr, 20);
                }

                if ($_SERVER["REQUEST_METHOD"] == "POST") {
                    $input = $_POST["input_string"];
                    $base20Hash = md5_to_base20($input);

                    $num20 = 0;
                    $diceResults = [];
                    if ($base20Hash === "000000000000000000000000000000") {
                        echo "<h1>You win!!! flag{}</h1>";
                        $num20 = 30;
                        $diceResults = array_fill(0, 30, 20);
                    } else {
                        function base20ToDecimal($char)
                        {
                            return ctype_digit($char) ? intval($char) : ord(strtolower($char)) - ord('a') + 10;
                        }

                        for ($i = 0; $i < strlen($base20Hash); $i++) {
                            $digit = base20ToDecimal($base20Hash[$i]);
                            $dieValue = 20 - $digit;
                            if ($dieValue == 20)
                                $num20++;
                            $diceResults[] = $dieValue;
                        }
                    }

                    echo "<h3 id='rolling'>Rolling... 🎲</h3>";
                    echo "<div class='dice-container'>";
                    for ($row = 0; $row < 5; $row++) {
                        echo "<div class='dice-row'>";
                        for ($col = 0; $col < 6; $col++) {
                            $index = $row * 6 + $col;
                            $die = $diceResults[$index] ?? 1;
                            try {
                                $i = $row + random_int(0, 10);
                            } catch (RandomException $e) {
                                $i = $row + $col;
                            }
                            echo "<div style='--i: $i;' class='three-dee-dice rolling' data-value='$die'>
                                 <div class='three-dee-dice-face three-dee-dice-front'></div>
                                 <div class='three-dee-dice-face three-dee-dice-back'></div>
                                 <div class='three-dee-dice-face three-dee-dice-right'></div>
                                 <div class='three-dee-dice-face three-dee-dice-left'></div>
                                 <div class='three-dee-dice-face three-dee-dice-top'></div>
                                 <div class='three-dee-dice-face three-dee-dice-bottom'></div> 
                            </div>";
                        }
                        echo "</div>";
                    }
                    echo "</div>";
                    echo "<script>
                    function showDiceNumber(value, dieElement) {
                        dieElement.classList.remove('rolling');
                        dieElement.querySelector('.three-dee-dice-front').innerText = value;
                    }

                    setTimeout(() => {
                        document.querySelectorAll('.three-dee-dice').forEach((die) => {
                            let value = parseInt(die.getAttribute('data-value'));
		                showDiceNumber(value, die);
		                if (value == 20) {
		                    die.classList.add('green');
		                }
                            });
                    }, 3200);
                    
                    setTimeout(() => {
                        document.querySelector('#rolling').innerHTML = '$num20 20 rolls!';
	                }, 3200);
	                document.querySelector('#form').remove();
                    </script>";

                    file_put_contents("/tmp/round_complete", time());
                }

                ?>
            </div>
        </main>
    </div>

    <script>
        function setTimestamp() {
            document.getElementById("timestampInput").value = Math.floor(Date.now() / 1000);
        }
    </script>

</body>

</html>
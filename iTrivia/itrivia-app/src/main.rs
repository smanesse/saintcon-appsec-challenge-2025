#![warn(clippy::all, clippy::pedantic)]

use serde::Deserialize;
use std::time::Duration;
use web_sys::{wasm_bindgen::JsCast, window, HtmlInputElement};

use dioxus::{prelude::*, web::WebEventExt};

const FAVICON: Asset = asset!("/assets/favicon.ico");
const MAIN_CSS: Asset = asset!("/assets/styling/main.scss");
const _: Asset = asset!("/assets/saintcarnsolas.woff2");
const _: Asset = asset!("/assets/saintcarnsolas.woff");
const _: Asset = asset!("/assets/saintcarnsolas.ttf");
const _: Asset = asset!("/assets/saintcarnsolas.svg");
const _: Asset = asset!("/assets/saintcarnsolas.eot");
const _: Asset = asset!("/assets/saintcarnsolas.otf");

const SERVER_TRUE: &str = "TRUE";

#[derive(Debug)]
enum Endpoint {
    New,
    Next,
    Answer,
    Status,
}

impl std::fmt::Display for Endpoint {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Endpoint::New => write!(f, "new"),
            Endpoint::Next => write!(f, "next"),
            Endpoint::Answer => write!(f, "answer"),
            Endpoint::Status => write!(f, "status"),
        }
    }
}

fn main() {
    dioxus::launch(App);
}

#[derive(Clone, Copy)]
struct State {
    pub started: Signal<bool>,
    pub submitted: Signal<bool>,
    pub token: Resource<Result<String, String>>,
    pub user_answer: Signal<String>,
    pub question: Resource<Result<String, String>>,
    pub answer_result: Resource<Result<String, String>>,
    pub status: Resource<Result<Status, String>>,
}

#[derive(Deserialize, Debug)]
struct Status {
    pub game_over: bool,
    pub min_guess_delta: u64,
    pub allowed_questions: u8,
    pub trivia_results: Vec<QuestionResult>,
    // pub answers_given: u8,
}

#[derive(Deserialize, Debug)]
struct QuestionResult {
    pub correct: bool,
    // pub delta: u64,
    pub index: u8,
}

#[component]
fn App() -> Element {
    let base_url = use_signal(|| {
        window()
            .and_then(|win| win.location().origin().ok())
            .unwrap_or_else(|| String::from("http://localhost:6006"))
    });

    let started = use_signal(|| false);
    let mut submitted = use_signal(|| false);
    let mut user_answer = use_signal(String::new);

    let token: Resource<Result<String, String>> = use_resource(move || async move {
        if !started() {
            return Err(String::from("Not Started"));
        }

        let chars = reqwest::Client::new()
            .get(format!("{}/{}", base_url(), Endpoint::New))
            .send()
            .await
            .map_err(|e| e.to_string())?
            .bytes()
            .await
            .map_err(|e| e.to_string())?
            .to_vec();

        String::from_utf8(chars).map_err(|e| e.to_string())
    });
    let question = use_resource(move || async move {
        reqwest::Client::new()
            .get(format!("{}/{}", base_url(), Endpoint::Next))
            .header(
                "User",
                token().unwrap_or(Ok(String::new())).unwrap_or_default(),
            )
            .send()
            .await
            .map_err(|e| e.to_string())?
            .bytes()
            .await
            .map_err(|e| e.to_string())
            .and_then(|bytes| String::from_utf8(bytes.to_vec()).map_err(|e| e.to_string()))
    });
    let answer_result = use_resource(move || async move {
        if !submitted() {
            return Err(String::from("Not Submitted Yet"));
        }

        let response_bytes = reqwest::Client::new()
            .post(format!("{}/{}", base_url(), Endpoint::Answer))
            .body(user_answer().clone().into_bytes())
            .header(
                "User",
                token().unwrap_or(Ok(String::new())).unwrap_or_default(),
            )
            .send()
            .await
            .map_err(|e| e.to_string())?
            .bytes()
            .await
            .map_err(|e| e.to_string())?
            .to_vec();

        String::from_utf8(response_bytes).map_err(|e| e.to_string())
    });
    let status: Resource<Result<Status, String>> = use_resource(move || async move {
        if !started() || token().is_none() {
            return Err(String::from("Uninitialized"));
        }
        answer_result();
        question();

        let status = reqwest::Client::new()
            .get(format!("{}/{}", base_url(), Endpoint::Status))
            .header(
                "User",
                token().unwrap_or(Ok(String::new())).unwrap_or_default(),
            )
            .send()
            .await
            .map_err(|e| e.to_string())?
            .bytes()
            .await
            .map_err(|e| e.to_string())
            .and_then(|bytes| String::from_utf8(bytes.to_vec()).map_err(|e| e.to_string()))?;

        let status_deserialized: Status =
            serde_json::from_str(&status).map_err(|e| e.to_string())?;

        Ok(status_deserialized)
    });

    let _question_timer = use_resource(move || async move {
        if !started()
            || submitted()
            || token().is_none()
            || question().is_none()
            || status
                .read()
                .as_ref()
                .is_none_or(|x| x.as_ref().map(|s| s.game_over).unwrap_or(true))
        {
            return false;
        }
        gloo_timers::future::sleep(Duration::from_secs(5)).await;
        user_answer.set(user_answer_normalize(&user_answer()));
        submitted.set(true);
        true
    });

    use_context_provider(|| State {
        started,
        submitted,
        token,
        user_answer,
        question,
        answer_result,
        status,
    });

    rsx! {
        document::Link { rel: "icon", href: FAVICON }
        document::Link { rel: "stylesheet", href: MAIN_CSS }

        div { class: "carnival",
            header {
                h1 { " - iTrivia - " }
                p { "E-Z stuff" }
            }
            main {
                div { class: "game",
                    if !started() {
                        start_button {}
                    } else {
                        question_component {}
                    }
                }
            }
        }
    }
}

#[component]
fn status_component() -> Element {
    let state = use_context::<State>();
    let status_s = state.status.suspend()?;
    rsx! {
        if let Ok(status) = status_s.read().as_ref() {
            div { class: "status",
                div { class: "questions",
                    for i in 1..=(status.allowed_questions) {
                        {
                            let result = status
                                .trivia_results
                                .iter()
                                .find(|t| t.index == i)
                                .map_or("unanswered", |c| if c.correct { "correct" } else { "incorrect" });
                            rsx! {
                                div { class: result }
                            }
                        }
                    }
                }
            }
        }
    }
}

#[component]
fn question_component() -> Element {
    let state = use_context::<State>();
    rsx! {
        SuspenseBoundary {
            fallback: |_| rsx! {
                h2 { "Loading" }
            },
            {
                match state.status.suspend()?.read().as_ref() {
                    Ok(status) => rsx! {
                        question_text {}
                        if (state.submitted)() {
                            answer_result {}
                            if !status.game_over {
                                next_question {}
                            } else {
                                game_over_controls {}
                            }
                        } else {
                            question_timer_component {}
                            answer_form {}
                            answer_button {}
                        }
                        status_component {}
                    },
                    Err(e) => rsx! {
                        h2 { "An Error Occurred: {e}" }
                    },
                }
            }
        }
    }
}

#[component]
fn start_button() -> Element {
    let mut state = use_context::<State>();
    rsx! {
        button {
            id: "start",
            onclick: move |_| {
                state.started.set(true);
                state.token.restart();
                state.submitted.set(false);
                state.user_answer.set(String::new());
            },
            "Start the Game"
        }
    }
}

#[component]
fn question_text() -> Element {
    let state = use_context::<State>();
    let question = state.question.suspend()?;

    rsx! {
        div { class: "question",
            {
                match question() {
                    Ok(text) => rsx! {
                        h2 { "{text}" }
                    },
                    Err(error) => rsx! {
                        h2 { "Failed to load question: {error}" }
                    },
                }
            }
        }
    }
}

#[component]
fn answer_form() -> Element {
    let mut state = use_context::<State>();
    rsx! {
        form {
            onsubmit: move |e| {
                e.prevent_default();
                state.user_answer.set(user_answer_normalize(&(state.user_answer)()));
                state.submitted.set(true);
            },

            div { class: "glitch-input-wrapper",
                div { class: "input-container",
                    input {
                        r#type: "text",
                        pattern: "\\d*",
                        placeholder: "",
                        onpaste: move |e| {
                            e.prevent_default();
                        },
                        maxlength: 15,
                        required: true,
                        class: "holo-input",
                        oninput: move |e| {
                            let input_element = e
                                .as_web_event()
                                .target()
                                .and_then(|t| t.dyn_into::<HtmlInputElement>().ok());
                            let mut current = input_element.clone().map_or(String::new(), |i| i.value());
                            current = current.chars().filter(|c| c.is_numeric()).collect();
                            input_element.inspect(|i| i.set_value(&current));
                            state.user_answer.set(current);
                        },
                    }
                    label {
                        r#for: "guess",
                        "data-text": "Enter your guess",
                        class: "input-label",
                        "\n                                Enter your guess\n                            "
                    }
                    div { class: "input-border" }
                    div { class: "input-scanline" }
                    div { class: "input-glow" }
                    div { class: "input-data-stream",
                        div { style: "--i: 0;", class: "stream-bar" }
                        div { style: "--i: 1;", class: "stream-bar" }
                        div { style: "--i: 2;", class: "stream-bar" }
                        div { style: "--i: 3;", class: "stream-bar" }
                        div { style: "--i: 4;", class: "stream-bar" }
                        div { style: "--i: 5;", class: "stream-bar" }
                        div { style: "--i: 6;", class: "stream-bar" }
                        div { style: "--i: 7;", class: "stream-bar" }
                        div { style: "--i: 8;", class: "stream-bar" }
                        div { style: "--i: 9;", class: "stream-bar" }
                    }
                    div { class: "input-corners",
                        div { class: "corner corner-tl" }
                        div { class: "corner corner-tr" }
                        div { class: "corner corner-bl" }
                        div { class: "corner corner-br" }
                    }
                }
            }
        }
    }
}

#[component]
fn answer_button() -> Element {
    let mut state = use_context::<State>();
    rsx! {
        button {
            id: "answer-btn",
            onclick: move |_| {
                state.user_answer.set(user_answer_normalize(&(state.user_answer)()));
                state.submitted.set(true);
            },
            "Submit"
        }
    }
}

#[component]
fn answer_result() -> Element {
    let state = use_context::<State>();
    let result = state.answer_result.suspend()?;

    match result() {
        Ok(val) => {
            if val == SERVER_TRUE {
                rsx! {
                    div { class: "win-announcement",
                        h2 { class: "win-title", "🏆🎉 CORRECT! 🏆🎉" }
                    }
                }
            } else {
                // Parse "FALSE:123:45" format to extract correct answer and difference
                let mut parts = val.split(':').skip(1);
                let correct_answer = parts.next().unwrap_or("unknown");
                let difference = parts.next().unwrap_or("unknown");

                rsx! {
                    div { class: "incorrect-answer",
                        h2 { "That's not correct :(" }
                        p { class: "correct-answer-reveal",
                            "The correct answer was: "
                            span { class: "correct-value", "{correct_answer}" }
                        }
                        p { class: "difference-reveal",
                            "You were off by: "
                            span { class: "difference-value", "{difference}" }
                        }
                    }
                }
            }
        }
        Err(e) => rsx! {
            h2 { "An error occurred: {e}" }
        },
    }
}

#[component]
fn next_question() -> Element {
    let mut state = use_context::<State>();
    rsx! {
        button {
            id: "next-question",
            onclick: move |_| {
                state.question.restart();
                state.submitted.set(false);
                state.user_answer.set(String::from("0"));
            },
            "Next Question"
        }
    }
}

#[component]
fn game_over_controls() -> Element {
    let state = use_context::<State>();
    let status = state.status.suspend()?;
    let player_won = status
        .read()
        .as_ref()
        .is_ok_and(|s| s.trivia_results.iter().any(|c| c.correct));
    let min_delta = status
        .read()
        .as_ref()
        .map_or(String::from("An Infinite Amount"), |s| {
            s.min_guess_delta.to_string()
        });

    rsx! {
        div { class: "game-over-controls",
            if player_won {
                div { class: "victory-message",
                    h1 { class: "victory-title", "🎊 VICTORY! 🎊" }
                    p { class: "victory-text", "You are a trivia champion!" }
                    p { class: "victory-subtext", "Thanks for playing our challenge!" }
                }
            } else {
                div { class: "defeat-message",
                    p { class: "defeat-text", "Thanks for trying the challenge!" }
                    p { class: "defeat-subtext", "Better luck next time!" }
                    p { class: "defeat-subtext", "Your closest score was off by {min_delta}" }
                }
            }
        }
    }
}

#[component]
fn question_timer_component() -> Element {
    rsx! {
        div { class: "countdown",
            div { class: "time" }
            div { class: "back" }
        }
    }
}

fn user_answer_normalize(answer: &str) -> String {
    answer
        .parse::<usize>()
        .map(|u| format!("{u}"))
        .unwrap_or(String::from("0"))
}

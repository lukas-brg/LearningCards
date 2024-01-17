const LOCALS = {
    de: {
        show_backside: "Rückseite einblenden",
        hide_backside: "Rückseite ausblenden",
        hide_answer: "Antwort ausblenden",
        check_answer: "Prüfen",
        toc: "Inhalte",
        input_required: "Bitte gebe eine Antwort ein.",
        check_required: "Bitte wähle mindestens eine Antwort aus.",
    },

    en: {
        show_backside: "Show Backside",
        hide_backside: "Hide Backside",
        hide_answer: "Hide Answer",
        check_answer: "Check Answer",
        toc: "Contents",
        input_required: "Please enter an answer.",
        check_required: "At least one answer is required to be selected.",
    },
};

const lang = document.documentElement.lang;

var locals = LOCALS[lang];

var coll = document.getElementsByClassName("collapsible");
var i;

var tocBtn = document.getElementById("toc-btn");
if (tocBtn) {
    var content = document.getElementsByClassName("toc-content")[0];
    content.style.display = "block";
    tocBtn.innerText = "∧";
    tocBtn.addEventListener("click", () => {
        if (content.style.display === "block") {
            tocBtn.innerText = "∨";
            content.style.display = "none";
        } else {
            tocBtn.innerText = "∧";
            content.style.display = "block";
        }
    });
}

for (i = 0; i < coll.length; i++) {
    (btn = coll[i]).addEventListener("click", function () {
        this.classList.toggle("active");
        btn.innerText = this.classList.contains("active")
            ? locals["hide_backside"]
            : locals["show_backside"];
        console.log(this.classList);
        var content = this.nextElementSibling;
        if (content.style.display === "block") {
            content.style.display = "none";
        } else {
            content.style.display = "block";
        }
    });
}

var cards = document.getElementsByClassName("card");

for (let card of cards) {
    card.addEventListener("mouseover", () => {
        btn = card.querySelector('[name="btn"]');
        focused = document.activeElement;
        // Workaround to fix problem of text input losing focus when moving mouse outside of it
        // this way textboxes only lose focus when moving to another card
        if (!(focused.name === "answer_field" + card.id)) {
            btn.focus();
        }
        btn.classList.add("focused");
    });
    card.addEventListener("mouseout", () => {
        btn = card.querySelector('[name="btn"]');

        btn.classList.remove("focused");
    });
}

const body = document.querySelector(".markdown-body");
const style = getComputedStyle(body);
const textColor = style.color;
const greenColor = lightOrDark(textColor) == "dark" ? "green" : "lime";
const redColor = "red";

// light mode color: rgb(36, 41, 47)
// dark mode color: rgb(201, 209, 217)

const CHECK_MARK = "&#10004;";

function multiOnClick(id) {
    let form = document.getElementsByName("multiform" + id)[0];
    let btn = document.getElementById("multi_btn" + id);
    let choices = form.getElementsByClassName("choice");
    let content = form.getElementsByClassName("multicontent")[0];

    btn.classList.toggle("active");
    let clicked = btn.classList.contains("active");

    let noneSelected = true;
    for (let item of choices) {
        if (item.checked) noneSelected = false;
    }

    if (noneSelected && clicked) {
        btn.classList.toggle("active");
        alert(locals.check_required);
        return;
    }

    btn.value = !clicked ? locals.check_answer : locals.hide_answer;
    for (let item of choices) {
        let label = item.nextElementSibling;
        let isCorrect = item.value === "correct";
        if (clicked) {
            if (item.checked != isCorrect) {
                label.style.color = redColor;
            } else {
                if (item.checked) label.style.color = greenColor;
            }
        } else {
            item.checked = false;
            label.style.color = textColor;
        }
    }
    content.style.display = clicked ? "block" : "none";
}

function checkAnswer(answer, answerCorrect) {
    answer = answer.toLowerCase().replaceAll(/ |-|_/g, "");
    answerCorrect = answerCorrect.toLowerCase().replaceAll(/ |-|_/g, "");
    return answer === answerCorrect;
}

function answerOnClick(id) {
    let answerField = document.getElementsByName("answer_field" + id)[0];
    let answer = answerField.value;
    let answerSpan = document.getElementsByName("answer" + id)[0];
    let answerCorrect = answerSpan.innerText;
    let answerContent = document.getElementsByName("answer_content" + id)[0];
    let btn = document.getElementById("answer_btn" + id);
    btn.classList.toggle("active");

    clicked = btn.classList.contains("active");

    if (clicked) {
        answer = answer.trim();
        if (answer === "") {
            alert(locals.input_required);
            btn.classList.toggle("active");
            return;
        }
        btn.value = locals.hide_answer;
        answerCorrect = answerCorrect.trim();

        answerContent.style.display = "block";

        if (checkAnswer(answer, answerCorrect)) {
            answerSpan.style.color = greenColor;
        } else {
            answerSpan.style.color = redColor;
        }
    } else {
        answerContent.style.display = "none";
        answerField.value = "";
        btn.value = locals["check_answer"];
    }
}

function initializeClipboard(button) {
    let originalText = button.innerHTML;
    let clipboard = new ClipboardJS(button, {
        target: function (trigger) {
            return trigger.parentElement.querySelector("code");
        },
    });

    clipboard.on("success", function (event) {
        let notification = event.trigger.previousElementSibling;
        console.log("copied:" + event.text);

        event.trigger.innerHTML = CHECK_MARK;
        event.trigger.style.color = "#3fb950";

        notification.style.display = "block";

        setTimeout(function () {
            event.trigger.innerHTML = originalText;
            event.trigger.style.color = "";
            notification.style.display = "none";
        }, 1500);

        event.clearSelection();
    });
}

document.querySelectorAll(".btn-copy").forEach(function (button) {
    initializeClipboard(button);
});

function lightOrDark(color) {
    // source: https://gist.github.com/krabs-github/ec56e4f1c12cddf86ae9c551aa9d9e04
    // Check the format of the color, HEX or RGB?
    if (color.match(/^rgb/)) {
        // If HEX --> store the red, green, blue values in separate variables
        color = color.match(
            /^rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*(\d+(?:\.\d+)?))?\)$/
        );

        r = color[1];
        g = color[2];
        b = color[3];
    } else {
        // If RGB --> Convert it to HEX: http://gist.github.com/983661
        color = +(
            "0x" + color.slice(1).replace(color.length < 5 && /./g, "$&$&")
        );

        r = color >> 16;
        g = (color >> 8) & 255;
        b = color & 255;
    }

    // HSP equation from http://alienryderflex.com/hsp.html
    hsp = Math.sqrt(0.299 * (r * r) + 0.587 * (g * g) + 0.114 * (b * b));

    // Using the HSP value, determine whether the color is light or dark
    if (hsp > 127.5) {
        return "light";
    } else {
        return "dark";
    }
}

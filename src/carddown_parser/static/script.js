

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

const locals = LOCALS[lang];

const iconTocUp =
    '<svg xmlns="http://www.w3.org/2000/svg" class="icon toc-icon toc-up" viewBox="0 0 512 512"><!--!Font Awesome Free 6.5.1 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2024 Fonticons, Inc.--><path d="M233.4 105.4c12.5-12.5 32.8-12.5 45.3 0l192 192c12.5 12.5 12.5 32.8 0 45.3s-32.8 12.5-45.3 0L256 173.3 86.6 342.6c-12.5 12.5-32.8 12.5-45.3 0s-12.5-32.8 0-45.3l192-192z"/></svg>';

const iconTocDown =
    '<svg xmlns="http://www.w3.org/2000/svg" class="icon toc-icon toc-down" viewBox="0 0 512 512"><!--!Font Awesome Free 6.5.1 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2024 Fonticons, Inc.--><path d="M233.4 406.6c12.5 12.5 32.8 12.5 45.3 0l192-192c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L256 338.7 86.6 169.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3l192 192z"/></svg>';


const iconCopy = '<svg xmlns="http://www.w3.org/2000/svg" class="icon copy-icon" viewBox="0 0 448 512"><!--!Font Awesome Free 6.5.1 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2024 Fonticons, Inc.--><path d="M384 336H192c-8.8 0-16-7.2-16-16V64c0-8.8 7.2-16 16-16l140.1 0L400 115.9V320c0 8.8-7.2 16-16 16zM192 384H384c35.3 0 64-28.7 64-64V115.9c0-12.7-5.1-24.9-14.1-33.9L366.1 14.1c-9-9-21.2-14.1-33.9-14.1H192c-35.3 0-64 28.7-64 64V320c0 35.3 28.7 64 64 64zM64 128c-35.3 0-64 28.7-64 64V448c0 35.3 28.7 64 64 64H256c35.3 0 64-28.7 64-64V416H272v32c0 8.8-7.2 16-16 16H64c-8.8 0-16-7.2-16-16V192c0-8.8 7.2-16 16-16H96V128H64z"/></svg>';


const body = document.body;
const style = getComputedStyle(body);
const textColor = style.color;
const greenColor = lightOrDark(textColor) == "dark" ? "green" : "lime";

const redColor = "red";

// light mode color: rgb(36, 41, 47)
// dark mode color: rgb(201, 209, 217)

const CHECK_MARK = "&#10004;";


for(let icon of document.querySelectorAll(".btn-copy")){
    icon.innerHTML = iconCopy;
}

var tocBtn = document.getElementById("toc-btn");
if (tocBtn) {
    var content = document.getElementsByClassName("toc-content")[0];
    tocBtn.innerHTML = iconTocUp;
    tocBtn.style.fill = "white";
    content.style.display = "block";

    tocBtn.addEventListener("click", () => {
        if (content.style.display === "block") {
            tocBtn.innerHTML = iconTocDown;
            content.style.display = "none";
        } else {
            tocBtn.innerHTML = iconTocUp;
            content.style.display = "block";
        }
    });
}

for (let btn of document.getElementsByClassName("collapsible")) {
    btn.addEventListener("click", function () {
        this.classList.toggle("active");
        btn.innerText = this.classList.contains("active")
            ? locals["hide_backside"]
            : locals["show_backside"];

        var content = this.nextElementSibling;
        if (content.style.display === "block") {
            content.style.display = "none";
        } else {
            content.style.display = "block";
        }
    });
}

for (let card of document.getElementsByClassName("card")) {
    card.addEventListener("mouseover", () => {
        btn = card.querySelector(".card-btn");
        focused = document.activeElement;

        if (!(focused.name === "answer_field" + card.id)) {
            btn.focus();
        }
        btn.classList.add("focused");
    });
    card.addEventListener("mouseout", () => {
        btn = card.querySelector(".card-btn");

        btn.classList.remove("focused");
    });
}

function multiOnClick(btn) {
    let form = btn.parentElement;

    let choices = Array.from(form.querySelectorAll(".choice"));
    let content = form.querySelector(".multicontent");

    btn.classList.toggle("active");
    let clicked = btn.classList.contains("active");

    let noneSelected = !choices.some(checkbox => checkbox.checked);

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

function answerOnClick(btn) {
    let form = btn.parentElement;

    let answerField = form.children[0];

    let answer = answerField.value;
    let answerContent = form.nextElementSibling;
    let answerSpan = answerContent.querySelector(".answer-span");
    let answerCorrect = answerSpan.innerText;

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
            event.trigger.innerHTML = iconCopy;
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

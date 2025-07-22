const img = document.querySelector(".css-hhc1wx img");

if (img) {
    img.removeAttribute("style");
    img.style.maxHeight = "51px";
    img.style.setProperty("max-height", "51px", "important");
}

window.addEventListener("chainlit-call-fn", (e) => {
    const { name, args, callback } = e.detail;
    if (name === "url_query_parameter") {
        callback(new URLSearchParams(window.location.search).get(args.msg));
    }
});

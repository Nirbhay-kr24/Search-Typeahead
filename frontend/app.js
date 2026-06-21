const input =
document.getElementById(
    "searchInput"
);

const suggestions =
document.getElementById(
    "suggestions"
);

const result =
document.getElementById(
    "result"
);

const trending =
document.getElementById(
    "trending"
);

let timer = null;

input.addEventListener(
    "input",
    () => {

        clearTimeout(timer);

        timer = setTimeout(
            loadSuggestions,
            300
        );
    }
);

async function loadSuggestions(){

    const q = input.value;

    if(!q){

        suggestions.innerHTML = "";

        document.getElementById(
            "latency"
        ).innerText = "0 ms";

        document.getElementById(
            "source"
        ).innerText = "-";

        return;
    }

    const res =
    await fetch(
        `http://127.0.0.1:8000/suggest?q=${q}`
    );

    const data =
    await res.json();

    document.getElementById(
        "latency"
    ).innerText =
        `${data.latency_ms} ms`;

    document.getElementById(
        "source"
    ).innerText =
        data.source;

    suggestions.innerHTML = "";

    data.results.forEach(item => {

        const div =
        document.createElement("div");

        div.className =
        "suggestion";

        div.innerText =
        item.query;

        div.onclick = () => {

            input.value =
            item.query;

            suggestions.innerHTML = "";
        };

        suggestions.appendChild(div);
    });
}

document
.getElementById("searchBtn")
.addEventListener(
"click",
search
);

async function search(){

    const q =
    input.value;

    const res =
    await fetch(
        "http://127.0.0.1:8000/search",
        {
            method:"POST",
            headers:{
                "Content-Type":
                "application/json"
            },
            body:JSON.stringify({
                query:q
            })
        }
    );

    const data =
    await res.json();

    result.innerHTML =
    data.message;

    loadTrending();
}

async function loadTrending(){

    const res =
    await fetch(
        "http://127.0.0.1:8000/trending"
    );

    const data =
    await res.json();

    trending.innerHTML="";

    data.forEach(item=>{

        const div =
        document.createElement("div");

       div.innerText =
        `${item.query}
        (${item.count})`;

        trending.appendChild(div);
    });
}

loadTrending();


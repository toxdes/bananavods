// for data
const DB_GIST_ID = "ce8969f8179882c88f6be79549f4d77b";

// cache data so we only fetch the API once per reload
var videos;

async function getVideos() {
  if (videos) return videos;
  let res = await fetch(`https://api.github.com/gists/${DB_GIST_ID}`);
  res = await res.json();
  const data = JSON.parse(res?.files["data.json"]?.content);
  return data;
}

const searchInput = document.getElementById("search-input");

function capitalize(s) {
  return s[0].toUpperCase() + s.slice(1);
}

function onTextChange(e) {
  const t = e.target.value;
  if (t == "") {
    getVideos().then((videos) => setResults(videos?.items));
  } else {
    getVideos().then((videos) => {
      const filterFn = getFilterFn(t);
      setResults(videos?.items?.filter(filterFn));
    });
  }
}

searchInput.addEventListener("input", onTextChange);

function getFilterFn(query) {
  return function (video) {
    let wordsExistInBoth = query
      ?.toLowerCase()
      ?.split(" ")
      ?.filter((e) => {
        let res = false;
        if (e) {
          video.title
            ?.toLowerCase()
            ?.split(" ")
            ?.filter((e1) => e1)
            ?.forEach((e1) => {
              if (e.length > 1 && e1.includes(e)) {
                res = true;
              } else if (e.length === 1 && e1 === e) {
                res = true;
              }
            });
        }
        return res;
      });
    return query.split(" ").filter((e) => e).length === wordsExistInBoth.length;
  };
}

function setResults(items) {
  const results = document.getElementById("results");
  results.innerHTML = null;
  if (!items || items?.length === 0) {
    results.innerHTML = `<p style="color:white;">Nothing to show.</p>`;
    return;
  }
  items.forEach((item) => {
    const child = document.createElement("div");
    child.role = "button";
    child.classList.add("result");
    child.onclick = function () {
      window.open(item.url, "_blank");
    };
    const img = document.createElement("img");
    img.src = item.thumbnail;
    img.alt = "thumbnail";
    img.classList.add("thumbnail");
    const link = document.createElement("p");
    link.innerText = item.title;
    const externalUrlIcon = document.createElement("div");
    externalUrlIcon.classList.add("icon");
    externalUrlIcon.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" x="0px" y="0px"
    width="18" height="18"
    viewBox="0,0,256,256">
    <g fill-rule="nonzero" stroke="none" stroke-width="1" stroke-linecap="butt" stroke-linejoin="miter" stroke-miterlimit="10" stroke-dasharray="" stroke-dashoffset="0" font-family="none" font-weight="none" font-size="none" text-anchor="none" style="mix-blend-mode: normal"><g transform="scale(10.66667,10.66667)"><path d="M5,3c-1.09306,0 -2,0.90694 -2,2v14c0,1.09306 0.90694,2 2,2h14c1.09306,0 2,-0.90694 2,-2v-7h-2v7h-14v-14h7v-2zM14,3v2h3.58594l-9.29297,9.29297l1.41406,1.41406l9.29297,-9.29297v3.58594h2v-7z"></path></g></g>
    </svg>`;
    child.appendChild(img);
    child.appendChild(link);
    child.appendChild(externalUrlIcon);
    results.appendChild(child);
  });
}

function setUpdatedAt(updatedAt) {
  const p = document.getElementById("last-updated");
  p.innerText = `Last updated: ${new Date(updatedAt).toDateString()}`;
}
getVideos().then((vids) => {
  videos = vids;
  setUpdatedAt(videos.updated_at);
  setResults(videos.items);
});

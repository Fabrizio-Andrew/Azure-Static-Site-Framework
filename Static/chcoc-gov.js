document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('#fetch').onclick = () => fetchBlobs();
});

function fetchBlobs() {
    fetch("https://blobstorageappstorage.blob.core.windows.net/convertedimages/?restype=container&comp=list")
    .then(response => response.text())
    .then(str => new window.DOMParser().parseFromString(str, "text/xml"))
    .then(xml => {
        let blobList = Array.from(xml.getElementsByTagName("Url"));
        console.log(blobList);
        blobList.forEach(async blobUrl => {
            console.log(blobUrl);
            var bloblink = document.createElement('a');
            bloblink.innerHTML = blobUrl.textContent;
            bloblink.href = blobUrl.textContent;

            document.querySelector('#bloblist').append(bloblink);
        });
    });
}


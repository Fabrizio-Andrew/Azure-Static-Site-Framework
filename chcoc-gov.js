document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('#fetch').onclick = () => fetchBlobs();
});

function fetchBlobs() {
    fetch("https://blobstorageappstorage.blob.core.windows.net/convertedimages/?restype=container&comp=list")
    .then(response => response.text())
    .then(str => new window.DOMParser().parseFromString(str, "text/xml"))
    .then(xml => {
        let blobList = Array.from(xml.querySelectorAll("Blobs"));
        console.log(blobList);
        blobList.forEach(async blobUrl => {
            console.log(blobUrl);
        });
    });
}


function jsmeOnLoad() {
    document.jsme = new JSApplet.JSME("jsme-box", "100%", "100%", {
        "options": "fullScreenIcon",
    });
}

let editorModalEl = document.getElementById('editorModal');
editorModalEl.addEventListener('shown.bs.modal', function (event) {
    document.getElementById("jsme-box").style.display = "inline";
    document.jsme.repaint();
});

function clearInput() {
    document.getElementById("id_identifier").value = "";
}

function insertSmiles() {
    document.getElementById("id_identifier").value = document.jsme.smiles();
}

function insertStructure() {
    let identifier = encodeURIComponent(document.getElementById("id_identifier").value);
    fetch("/chemical/structure/" + identifier + "/file?format=jme", {
        method: 'get',
        headers: {
            'Accept': 'text/plain',
            'Content-Type': 'text/plain'
        }
    }).then(async (response) => {
        if (response.ok) {
            let data = await response.text();
            console.log(data);
            document.jsme.readMolecule(data);
        } else {
            console.log("response has no ok status")
        }
    }).catch((error) => {
        console.log(error)
    })
}

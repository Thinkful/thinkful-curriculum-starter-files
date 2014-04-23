var Chords = function() {
    this.wavesurfer = Object.create(WaveSurfer);
    this.wavesurfer.init({container: '#waveform'});
    this.wavesurfer.load("static/audio/azoora.mp3");

    this.playButton = $("#play-button");
    this.playIcon = $("#play-button i");
    this.playButton.click(this.onPlayButtonClicked.bind(this));
    this.playing = false;

    this.addButton = $("#add-button");
    this.addButton.click(this.onAddButtonClicked.bind(this));

    this.fileInput = $("#file-input");
    this.fileInput.change(this.onFileAdded.bind(this));

    this.uploadForm = $("#upload-form");

    this.getSongs();
};

Chords.prototype.onPlayButtonClicked = function() {
    if (this.playing) {
        this.wavesurfer.pause();
    }
    else {
        this.wavesurfer.play();
    }
    this.playing = !this.playing;
    this.playIcon.toggleClass("fa-play");
    this.playIcon.toggleClass("fa-pause");
};

Chords.prototype.onAddButtonClicked = function() {
    this.fileInput.click();
};

Chords.prototype.onFileAdded = function(event) {
    var file = this.fileInput[0].files[0];
    var name = file.name;
    var size = file.size;
    var type = file.type;

    var data = new FormData(this.uploadForm[0]);
    var ajax = $.ajax('/api/files', {
        type: 'POST',
        xhr: this.createUploadXhr.bind(this),
        data: data,
        cache: false,
        contentType: false,
        processData: false,
        dataType: 'json'
    });
    ajax.done(this.onUploadDone.bind(this));
    ajax.fail(this.onUploadFail.bind(this));
};

Chords.prototype.createUploadXhr = function() {
    var xhr = new XMLHttpRequest();
    if(xhr.upload) { // if upload property exists
        xhr.upload.addEventListener('progress',
                                    this.onUploadProgress.bind(this), false);
    }
    return xhr;
};

Chords.prototype.onUploadDone = function(data) {
    console.log("Uploading file succeeded");
    data = {
        file: {
            id: data.id
        }
    }
    var ajax = $.ajax('/api/songs', {
        type: 'POST',
        data: JSON.stringify(data),
        contentType: 'application/json',
        dataType: 'json'
    });
    ajax.done(this.onAddSongDone.bind(this));
    ajax.fail(this.onAddSongFail.bind(this));
};

Chords.prototype.onUploadFail = function(event) {
    console.error("File upload failed: ", event.statusText);
};

Chords.prototype.onAddSongDone = function(data) {
    console.log("Adding song succeeded");
};

Chords.prototype.onAddSongFail = function(data) {
    console.error("Adding song failed: ", event.statusText);
};

Chords.prototype.onUploadProgress = function(event) {
};

Chords.prototype.getSongs = function() {
    var ajax = $.ajax('/api/songs', {
        type: 'GET',
        dataType: 'json'
    });
    ajax.done(this.onGetSongsDone.bind(this));
    ajax.fail(this.onGetSongsFail.bind(this));
};

$(document).ready(function() {
    window.app = new Chords();
});

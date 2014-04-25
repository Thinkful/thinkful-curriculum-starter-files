var Chords = function() {
    this.wavesurfer = Object.create(WaveSurfer);
    this.wavesurfer.init({container: '#waveform'});
    this.wavesurfer.on("mark", this.setChord.bind(this));

    this.playButton = $("#play-button");
    this.playIcon = $("#play-button i");
    this.playButton.click(this.onPlayButtonClicked.bind(this));
    this.playing = false;

    $("#songs").on("click", ".song",
                   this.onSongClicked.bind(this));
    $("#songs").on("click", "#add-button",
                   this.onAddButtonClicked.bind(this));

    this.fileInput = $("#file-input");
    this.fileInput.change(this.onFileAdded.bind(this));

    this.uploadForm = $("#upload-form");

    this.songList = $("#song-list");
    this.songListTemplate = Handlebars.compile($("#song-list-template").html());

    this.songs = [];
    this.getSongs();

    this.chords = null;
};

Chords.prototype.onSongClicked = function(event) {
    this.pause();
    this.wavesurfer.clearMarks();
    var song = $(event.target);
    this.wavesurfer.load(song.data("path"));

    var ajax = $.ajax('/api/songs/' + song.data('id') + '/chords', {
        type: 'GET',
        dataType: 'json'
    });
    ajax.done(this.onGetChordsDone.bind(this));
    ajax.fail(this.onFail.bind(this, "Getting chords"));
};

Chords.prototype.onGetChordsDone = function(data) {
    chords = data;
    var duration = this.wavesurfer.getDuration();
    for (var i=0; i<chords.length; i++) {
        var chord = chords[i];
        if (chord.time == 0) {
            continue;
        }

        var mark = this.wavesurfer.mark({
            position: chord.time * duration,
            color: 'rgba(0, 255, 0, 0.5)'
        });
        mark.chord = chord.chord;
    }
};

Chords.prototype.setChord = function(mark) {
    $("div#chord div div").text(mark.chord);
};

Chords.prototype.onPlayButtonClicked = function() {
    if (this.playing) {
        this.pause();
    }
    else {
        this.play();
    }
};

Chords.prototype.togglePlayIcon = function() {
    this.playIcon.toggleClass("fa-play");
    this.playIcon.toggleClass("fa-pause");
};

Chords.prototype.play = function() {
    if (this.playing) {
        return;
    }
    this.wavesurfer.play();
    this.togglePlayIcon();
    this.playing = true;
};

Chords.prototype.pause = function() {
    if (!this.playing) {
        return;
    }
    this.wavesurfer.pause();
    this.togglePlayIcon();
    this.playing = false;
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
    ajax.fail(this.onFail.bind(this, "File upload"));
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
    ajax.fail(this.onFail.bind(this, "Adding song"));
};

Chords.prototype.onAddSongDone = function(data) {
    this.songs.push(data);
    this.updateSongView();
};

Chords.prototype.onUploadProgress = function(event) {
};

Chords.prototype.getSongs = function() {
    var ajax = $.ajax('/api/songs', {
        type: 'GET',
        dataType: 'json'
    });
    ajax.done(this.onGetSongsDone.bind(this));
    ajax.fail(this.onFail.bind(this, "Getting song information"));
};

Chords.prototype.onGetSongsDone = function(data) {
    this.songs = data;
    this.updateSongView();
};

Chords.prototype.updateSongView = function() {
    var context = {
        songs: this.songs
    };

    var songList = $(this.songListTemplate(context));
    this.songList.replaceWith(songList);
    this.songList = songList;
};

Chords.prototype.onFail = function(what, event) {
    console.error(what, "failed: ", event.statusText);
};

$(document).ready(function() {
    window.app = new Chords();
});

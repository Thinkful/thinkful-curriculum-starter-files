var Chords = function() {
    this.wavesurfer = Object.create(WaveSurfer);
    this.wavesurfer.init({container: '#waveform'});
    this.wavesurfer.load("static/audio/azoora.mp3");
};

$(document).ready(function() {
    window.app = new Chords();
});

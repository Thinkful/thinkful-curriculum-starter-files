var gulp = require('gulp');
var marked = require('gulp-marked');
var flatten = require('gulp-flatten');
var gutil = require('gulp-util');
var glob = require('glob');
var concat = require('gulp-concat');
// var jsdom = require("jsdom").jsdom;


source = {
	assignments: './units/**/lessons/**/assignments/*.md',
	assets: './units/**/lessons/**/assignments/assets/*.{jpg,png}',
	intros: ['./intro.md', './units/**/intro.md', './units/**/lessons/**/intro.md']
};

build = {
	build: './build/',
	assetsFolder:'./build/assets/', 
	xmlFolder: './build/xmlPartials/'
};



gulp.task('default', ['gatherAssets', 'buildIntros', 'buildAssignments']);

gulp.task('buildAssignments', function () {
    return gulp.src(source.assignments)
    	.pipe(marked({
    		renderer: rendererConfig,
    		
    		// ### WE SHOULD ## be moving hljs out of Angular and into build process    		//
    		// highlight: function (code, lang) {
    		// 	gutil.log(code);	
   			// 	 return require('highlight.js').highlight(code, lang).value; // need to get this working, circumvent highlight in ang directive altogether
  				// }
    	}))
        .pipe(gulp.dest(build.xmlFolder)); 
});

gulp.task('buildIntros', function() {
	return gulp.src(source.intros)
		.pipe(marked({
			renderer: rendererConfig
		}))
		.pipe(gulp.dest(build.xmlFolder));
})

gulp.task('gatherAssets', function(){
  return gulp.src(source.assets)
  	.pipe(flatten())
    .pipe(gulp.dest(build.assetsFolder));
});



function escape(html, encode) {
  return html
    .replace(!encode ? /&(?!#?\w+;)/g : /&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

var rendererConfig = {
	
	heading: function (text, level) {
		
		var tags = ['<h' + level + '>', '</h' + level + '>\n'];
		
		if (level===1) {
			tags = ['<name>', '</name>\n']
		}
		
		else if (level==2) {
			tags = ['<header>', '</header>\n']
		}
		
		return tags[0] + text + tags[1];
	},
	image: function(href, title, text) {
		return '<img source="' + href + '" asset>';
	},

	link: function(href, title, text) {
		return '<a href="' + href + '" target="_blank">' + text + '</a>';
	},
	
	code: function(code, language) {
		
		return '<codesnippet language="' + language + '">' + escape(code) + '</codesnippet>\n';
	},
		
};

var gulp = require('gulp');
var marked = require('gulp-marked');
var flatten = require('gulp-flatten');
var gutil = require('gulp-util');

source = {
	assignments: './units/**/lessons/**/assignments/*.md',
	courseIntro: './intro.md',
	unitIntros: './units/**/intro.md',
	lessonIntros: './units/**/lessons/**/intro.md',
	assets: './units/**/lessons/**/assignments/assets/*.{jpg,png}'
};

build = {
	assetsFolder:'./build/assets/', 
	xmlFolder: './build/xmlPartials/'
};

gulp.task('buildXML', function () {
    return gulp.src(source.assignments)
    	.pipe(marked())
        .pipe(gulp.dest(build.xmlFolder)); 
});

gulp.task('gatherAssets', function(){
  return gulp.src(source.assets)
  	.pipe(flatten())
    .pipe(gulp.dest(build.assetsFolder));
});

function escapeCode(code) {
	gutil.log(code);
	return code.replace(/>/g, '&gt;')
		.replace(/</g, '&lt;')
		.replace(/&/g, '&amp;');
}


var rendererConfig = {
	
	// heading: function (text, level) {
		
	// 	var tags = ['<h' + level + '>', '</h' + level + '>'];
		
	// 	if (level===1) {
	// 		tags = ['<name>', '</name>']
	// 	}
		
	// 	else if (level==2) {
	// 		tags = ['<header>', '</header>']
	// 	}
		
	// 	return tags[0] + text + tags[1];
	// },
	// // image: function(href, title, text) {
	// // 	return '<p><img source="' + href + '" asset></p>';
	// // },

	// // link: function(href, title, text) {
	// // 	return '<a href="' + href + '" target="_blank">' + text + '</a>';
	// // },
	
	// // code: function(code, language) {
	// // 	return '<codesnippet language="' + language + '>' + code + '</codesnippet>';
	// // },

	// if header and stripped is equal to "Comprehension Check", then add comprehension check class to it
	// then we just style this. target sibling ul/ol of h4s with 'comprehension-check' class
		
};

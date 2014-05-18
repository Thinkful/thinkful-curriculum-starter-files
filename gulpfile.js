var gulp = require('gulp');
var marked = require('gulp-markdown')
var flatten = require('gulp-flatten');
	// gulp.task('copy-fonts', function() {
	//   gulp.src('dependencies/**/*.{ttf,woff,eof,svg}')
	//   .pipe(flatten())
	//  .pipe(gulp.dest('build/fonts'));
	// });



source = {
	assignments: './units/**/lessons/**/assignments/*.md',
	courseIntro: './intro.md',
	unitIntros: './units/**/intro.md',
	lessonIntros: './units/**/lessons/**/intro.md',
	assets: './units/**/lessons/**/assignments/assets/*.{jpg,png}'
};

build = {
	assetsFolder:'./build/assets/' 
};


// gulp.task('buildXML', function () {
//     return gulp.src(source.assignments)
//         .pipe(convertMarkdown({renderer: rendererConfig}))
//         .pipe(gulp.dest('./build')); // need to keep running track of file names and location in hierarchy so can write to a doc
// });

gulp.task('gatherAssets', function(){
  return gulp.src(source.assets)
  	.pipe(flatten())
    .pipe(gulp.dest(build.assetsFolder));
});

function escapeCode(code) {
	return code.replace(/>/g, '&gt;')
		.replace(/</g, '&lt;')
		.replace(/&/g, '&amp;');
}




// var rendererConfig = {
// 	heading: function (text, level) {

// 		// by default escaped text of block lev is added as id
// 		// var escapedText = text.toLowerCase().replace(/[^\w]+/g, '-');
		
// 		var tags = ['<h' + level + '>', '</h' + level + '>'];
// 		if (level===1) {
// 			tags = ['<name>', '</name>']
// 		}
// 		else if (level==2) {
// 			tags = ['<header>', '</header>']
// 		}
// 		return tags[0] + text + tags[1];
// 	},
// 	image: function(href, title, text){
// 			return '<p><img source="' + href + '" asset></p>';
// 		}

// 		renderer.link = function(href, title, text) {
// 			return '<a href="' + href + '" target="_blank">' + text + '</a>';
// 		}

// 		renderer.code = function(code, language) {
// 			return '<codesnippet language="' + language + '>' + code + '</codesnippet>';
// 		}
// 	},
// 	code: function() {
// 		//escapeCode()
// 	},

// 	link: function() {

// 	},

// 	// if header and stripped is equal to "Comprehension Check", then add comprehension check class to it
// 	// then we just style this. target sibling ul/ol of h4s with 'comprehension-check' class

// 	var x = "## v2: Maintain Curricula and Enable Metadata/ Tagging\n" +"```xml\n<html>{{ hia }}</html>\n```"  		
// 	console.log(marked(x, { renderer: renderer }));
		
// 	});

// };
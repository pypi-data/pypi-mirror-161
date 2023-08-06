# templ8

templ8 is a templating software for websites designed with lightweightness, flexibility and ease of use in mind. It was also designed with the idea that one's website is one's temple, so a lot of the terminology is thematic with that. Sticking to this thematic is very hard because I also want to bring in Ampersandia and We Know The Devil references into the mix, which don't mix well with the original idea. I honestly don't care about that problem, though.

The previous version, which I call templ8.0 was extremely tedious to use and designed only for me. This one is an improvement in those regards (not that it being designed for my own projects makes it bad, but it'd be cool to make it generalizable).

It supports [Textile](textile-lang.org), [Kami](github.com/lilith-in-starlight/kami-parser) and Markdown. It detects which format you want to use by checking the files' extensions.

It's currently being made, so I don't expect this to be functional or fully usable. And the code is bad. It will probably remain bad, but I'll try to make it okay over time.

[My website](ampersandia.net) is made with this tool.

## Installing
Simply run `pip install templ8` and make sure that the scripts directory of your python install scheme is in path.

## Roadmap
*Or, i try to pretend i have an organized plan for this project (i dont)*

This roadmap is as chronologically ordered as homestuck (i'm _pretty sure_ that it isn't ordered but honestly good luck.)

- [x] Basic templating functionality like templ8.0's
- [x] Easier-to-customize replacement tags
- [x] Copy non-markup files from the input folder into the output
- [x] txignore file for textile files that should be put on the output folder unprocessed
- [x] Customizing "core" file and directory names of a project
- [X] Change a specific page's basehtml
- [X] Markdown support
- [X] IFKEYs for further basetemplate flexibility (UNSTABLE)
- [X] Blogging
- [ ] RSS and ASS feed generating tool

## Crash Course
*Or, i try so fucking hard to make this program make sense*

### Commands
templ8 currently has two commands:

- `templ8 help (command)`: Shows help for the (command). The (command) is optional.
- `templ8 genesis [dirname]`: Creates a new directory named `[dirname]` with basic files required for templ8's functionality.
- `templ8 divine`: Assembles the current project into a website in the output folder. Requires a `d8y` file to be in the current directory. It also copies non-textile files to the output.
- `templ8 radio`: Assembles a blog. It's the worst blogging tool you have ever seen.
- `templ8 pandoc`: Installs pandoc, use it if you want to use markdown instead of textile. It may error and still work. I don't know why.

### How does it work?
Put the templ8.py file in an empty folder. Make a file called `d8y` with no extension, a file called `basehtml`, also with no extension, and two folders, `input` and `output`.

You might also want one called `repl8ce`, with no extension.

The `basehtml` file is an html file in which templ8.py puts the content of your pages. It tells templ8 how your page should look: Whatever you put in it, will be there in every page.

Somewhere in `basehtml`'s body should be a line that only says `##CONTENT##`. This is what templ8 will replace for the content.

`/input/index.textile`
```textile
example paragraph with some html stuff
```

`/basehtml`
```html
<html>
  <body>
	 ##CONTENT##
  </body>
</html>
```

`/output/index.html`
```html
<html>
  <body>
	 <p>example paragraph with some html stuff</p>
  </body>
</html>
```

#### Custom Replacement Keys

You can create custom `##KEYS##` in `rpl8cmnt`. They're parts of the basehtml that individual files can modify.

`/repl8ce`
```plaintext
PAGETITLE=A Default Title
CUSTOMKEY=Another default value
EMPTYKEY=
```

EMPTYKEY's default value is an empty string.

`/basehtml`
```html
...
<head>
<title>##PAGETITLE##</title>
</head>
...
```

`/input/index.html`
```plaintext
CUSTOMKEY=Non Default Value
-BEGINFILE-
the page's contents start here
```

`/output/index.html`
```html
...
<head>
<title>Non Default Value</title>
</head>
...
```

A custom key can be replaced with an empty string by doing `CUSTOMKEY=` with nothing after the equals. You can have multiline values by using this format:

```plaintext
;;KEY
Multi
line
value
```

All multiline keys must go after the single line keys.

#### Core Renaming
You can also rename the input, output, basehtml and repl8ce files using the d8y file. Simply do this, making sure your custom values don't start with a number and dont have spaces:

```plaintext
input=your_input_folder
output=your_output_folder
replace=your_replace_file
basehtml=your_basehtml_file
```

#### txignore
txignore files are like .gitignore files, except they don't mean "don't put this file on the ouput," it's more like "output the raw file." Putting a path to a directory in txignore will be non-recursive, and child directories will not be ignored. It also works for markdown files.

#### i want a blog now
You should just use another tool and somehow mix it with this, but if you want to insist in using this, templ8 already does its best to simplify what is otherwise a really tedious process.

Just run `templ8 radio` and this'll create a few folders: `blog` in the root of the project, `output/blog` and `output/blog/posts`; and a `blogbase` file also in the root.

Add textile files on the `blog` folder in the root, these'll be your posts. You don't need to add title or anything as the content, just use the keys `TITLE`, `AUTHORS`, `DATE`, `TAGS` and `INTRO`. INTRO is the one that will appear in the index file (the main page of your blog, where previews of all your articles will be).

This blog is static, so no pages nor search function of any kind. Just articles. If you want the articles to be chronologically ordered, name them something like `000000000001.textile` and increase the number for each new article. There's no core renaming for blog parts, blogs are already scuffed enough.

`blogbase` is what tells templ8 what the blog's most basic layout is. It's very messy to use, but I'll document how it works soon. If you want to use Markdown for your blog, change the it for this:

```markdown
PAGETITLE=##TITLE##
-BEGINFILE-
## ##TITLE##

^##AUTHORS## - ##TAGS## - ##DATE##^

##CONTENT##

-BEGININDEX-
## "##TITLE##":##LINK##

^##AUTHORS## - ##TAGS## - ##DATE##^

##INTRO##
-BEGININDEX-
PAGETITLE=Blog
```

#### i want a file to have a separate basehtml
Just add set your file's value of the `CUSTOMBASE` key to the path to your new basehtml. You don't need to set up this key in repl8ce.

## Versioning
*Or, roxy how the fuck am i supposed to tell which of these is newest*

Like most of my themed projects, templ8 doesn't use semver, it uses some variant of it made by me. It is unnecessary and potentially cumbersome, but I like doing it. Here I explain it.

Define X, Y and Z as positive integers representing major release, minor release and patch, respectively. The specifics of what counts as each are completely arbitrary and decided by the project manager (me). Express a version following these rules:

- If Z = 0 and Y = 0, then write it as `8.X`.
- If Z = 0, then write it as `8.X.Y`.
- In any other case, write as `8.X.Y.Z`.
- `templ` might be appended before a version, for example: `templ8.5.3`
- If you want to do whatever specific thing not outlined here, do whatever, just keep it looking like it follows these rules.
  - Or not. I'm not a cop. `π` is the best templ8 version.

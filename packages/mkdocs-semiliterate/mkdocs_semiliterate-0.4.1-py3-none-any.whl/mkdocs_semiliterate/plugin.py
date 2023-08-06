""" md
## Usage

Once this plugin is [installed](../README.md#installation), just replace
the plugin name `simple` with `semiliterate` in your `mkdocs.yml` file.
It accepts all of the same parameters, so `mkdocs` will still work as before,
and you will have immediate access to all of the following extensions.
(Note that this documentation assumes a familiarity with the
[usage](https://athackst.github.io/mkdocs-simple-plugin/mkdocs_simple_plugin/plugin/)
of the `simple` plugin.)
"""

from mkdocs import utils
from mkdocs.config import config_options
from mkdocs_simple_plugin.semiliterate import (
    Semiliterate, LazyFile, ExtractionPattern, StreamExtract, get_line)
from mkdocs_simple_plugin.plugin import SimplePlugin

import os
import re
import subprocess
import tempfile
import yaml


class FlextractionPattern(ExtractionPattern):
    r""" Extends ExtractionPattern to add ensure_line argument
to replace_line method.
    """
    # Following must be identical to ExtractionPattern.replace_line,
    # except as marked:
    def replace_line(self, line, ensure_line=True):
        """Apply the specified replacements to the line and return it."""
        if not self.replace:
            return line
        for item in self.replace:
            pattern = item[0] if isinstance(item, tuple) else item
            match_object = pattern.search(line)
            if match_object:
                # CHANGES HERE
                replaced = False
                replacement = ''
                if isinstance(item, tuple):
                    replacement = match_object.expand(item[1])
                    replaced = True
                elif match_object.lastindex:
                    replacement = match_object[match_object.lastindex]
                    replaced = True
                if replaced and ensure_line:
                    replacement = get_line(replacement)
                return replacement
                # END OF CHANGES
        # Otherwise, just return the line.
        return line


class StreamInclusion(StreamExtract):
    r""" md  An extension of the StreamExtract class which adds

### Inclusion syntax

While extracting content from a file (because it matches one of the
`semiliterate` patterns, rather than just one of the `include_extensions`),
an unescaped expression of the form

`{! FILENAME YAML !}`

(which may span multiple lines) will trigger file inclusion. The FILENAME may
be a bare word, in which case it cannot contain whitespace, or it may be
enclosed in single or double quotes. Note that FILENAME is interpreted relative
to the directory in which the file containing the `{! .. !}` expression
resides. The YAML is interpreted exactly as the extraction options to a
`semiliterate` item as
[documented](https://athackst.github.io/mkdocs-simple-plugin/mkdocs_simple_plugin/plugin/index.html#semiliterate)
for the `simple` extension, subject to the extensions below. The text
extracted from FILENAME is interpolated at the current location in the file
currently being written. Recursive inclusion is supported.

The simplest example of such an inclusion directive is just
`{! boilerplate.md !}`, which (because of the conventions for extraction
parameters) simply interpolates the entire contents of `boilerplate.md`
at the current location.

For an example that uses more of the extraction parameters, the current
version number of mkdocs-semiliterate is extracted into the
[Overview](../README.md) of this documentation via

` {! ../README.md extract: { start: 'repo:.*(\{!.*!\})', stop: '' }
terminate: Rationale
!}`

to take advantage of the beginning of the `setup.cfg` file:
```
{! ../setup.cfg terminate: long !}...
```

(and of course both of the code snippets just above are extracted into this
page with `{! ... !}`, as you can see in the
[source code](https://code.studioinfinity.org/glen/mkdocs-semiliterate/src/branch/main/mkdocs_semiliterate/plugin.py)
for the plugin.)

Note that a `{! ... !}` directive must be in a line that semiliterate would
normally copy. That is, semiliterate does not examine lines after
the `terminate` regexp, or when no mode of extraction is active.
It also doesn't check any text written from lines that match these
special expressions, including `start` and `stop`.
Moreover, on such normally-transcribed lines,
it's the text **after** the application of any semiliterate `replace`ments that
is checked for `{! ... !}`.
     """  # noqa: E501

    include_open = re.compile(r'''(?<![`\\])(\{\!\s*)([\s'"])''')
    include_quoted_file = re.compile(
        r'''(['"])(?P<fn>.*?)\1\s+(?P<yml>[\s\S]*?)\s?\!\}''')
    include_bare_file = re.compile(r'\s(?P<fn>.*?)\s+(?P<yml>[\s\S]*?)\s?\!\}')

    def __init__(self, input_stream, output_stream, include_root,
                 ensurelines=True, terminate=None, patterns=None, **kwargs):
        if terminate and not hasattr(terminate, 'search'):
            terminate = re.compile(terminate)
        # Unfortunately, "simple" has now moved the pattern parsing into
        # Semiliterate, so we need to reiterate the code for that here:
        if patterns is None:
            if 'extract' in kwargs:
                extract = kwargs.pop('extract')
                if isinstance(extract, dict):
                    extract = [extract]
                patterns = [FlextractionPattern(**p) for p in extract]
            else:
                patterns = [FlextractionPattern()]
        super().__init__(input_stream, output_stream,
                         terminate, patterns, **kwargs)
        self.include_root = include_root
        self.ensure_lines = ensurelines

    def extract_line(self, line, extraction_pattern):
        """Copy line to the output stream, applying all specified replacements
           and handling inclusion syntax.
        """
        line = extraction_pattern.replace_line(line, self.ensure_lines)
        include_match = StreamInclusion.include_open.search(line)
        if not include_match:
            self.transcribe(line)
            return
        # OK, we have found (the start of) an inclusion and must process it
        preamble = line[:include_match.start()]
        remainder = line[include_match.end(1):]
        doublequoted = False
        body_pattern = StreamInclusion.include_quoted_file
        if include_match[2].isspace():
            body_pattern = StreamInclusion.include_bare_file
        elif include_match[2] == '"':
            doublequoted = True
        body_match = body_pattern.search(remainder)
        if not body_match:
            for extra_line in self.input_stream:
                remainder += extraction_pattern.replace_line(extra_line,
                                                             self.ensure_lines)
                body_match = body_pattern.search(remainder)
                if body_match:
                    break
        if not body_match:
            errmsg = "semiliterate: End of file while scanning for `!}`"
            utils.log.error(errmsg)
            raise EOFError(errmsg)
        filename = body_match['fn']
        gitextract = False
        r""" md
### Double-quoted filenames and Git extraction

Standard Python escape sequences in double-quoted filenames are interpreted
as usual; for example you can write
```
{! ../tests/fixtures/quoted-filename/README.md extract:
  start: '(.*!.*)'
  stop: '\s'
!}
```
to include a file whose name (`snippet/Say "Don't"`, in this case) has both
double and single quotes.

Further, `semiliterate` supports a special escape to extract a file from the
Git archive of the project (presuming it is under Git version control) and then
include content from that file. For example, you could write
```
{! ../tests/fixtures/git-inclusion/README.md extract:
  start: '(.*!.*)'
  stop: '\s'
!}
```

to extract content starting after the `### install` line from the
`mkdocs.yml` file in the Git commit of this repository
tagged `0.1.0`. This feature is primarily useful if you are documenting the
development or changes to a project over time, or are documenting a feature
in a specific past release of your project, and want to be sure that
material included in your documentation does _not_ change as the project
progresses. (This behavior is as opposed to the usual case, in which you want
your documentation to incorporate the most up-to-date version of extracted
content.)

The precise behavior for a FILENAME argument in a `{! ... !}` inclusion of the
form

`"\git SPECIFIER"`

is that the output of `git show SPECIFIER` is written to a temporary file,
and that file is extracted from.
"""
        if doublequoted:
            if filename[:5] == r'\git ':
                gitextract = True
                filename = filename[5:]
            filename = (filename.encode('latin-1', 'backslashreplace')
                                .decode('unicode-escape'))
        include_path = self.include_root + '/' + filename
        if gitextract:
            (write_handle, include_path) = tempfile.mkstemp()
            utils.log.info(
                f"semiliterate: extracting {filename} to {include_path}")
            contents = subprocess.check_output(['git', 'show', filename])
            os.write(write_handle, contents)
            os.close(write_handle)
        new_root = re.match(r'(.*)/', include_path)[1]
        try:
            include_parameters = yaml.safe_load(body_match['yml'])
        except Exception as err:
            newmsg = (f"While attempting to include '{include_path}', could"
                      + f" not parse yaml '{body_match['yml']}'.")
            if hasattr(err, 'message'):
                raise SyntaxError(
                    f"{newmsg} YAML parser reports: {err.message}")
            raise SyntaxError(f"{newmsg} Caught exception: {str(err)}")
        if not include_parameters:
            include_parameters = {}
        with open(include_path) as include_file:
            self.transcribe(preamble)
            inclusion = StreamInclusion(
                include_file, self.output_stream, new_root,
                **include_parameters)
            if inclusion.extract():
                self.wrote_something = True
        self.transcribe(remainder[body_match.end():])

    # ## The following has to be identical to StreamExtract.check_pattern
    # ## except for the marked bit handling ensure_lines
    def check_pattern(self, pattern, line, emit_last=True):
        """Check if pattern is contained in line.

        If _pattern_ is not false-y and is contained in _line_,
        returns true (and if the _emit_last_ flag is true,
        emits the last group of the match if any). Otherwise,
        check_pattern does nothing but return false.
        """
        if not pattern:
            return False
        match_object = pattern.search(line)
        if not match_object:
            return False
        if match_object.lastindex and emit_last:
            # CHANGES HERE
            # self.transcribe(get_line(match_object[match_object.lastindex]))
            to_emit = match_object[match_object.lastindex]
            if self.ensure_lines:
                to_emit = get_line(to_emit)
            self.transcribe(to_emit)
        return True


class SemiliteratePlugin(SimplePlugin):
    r""" md   An extension of the mkdocs-simple-plugin

### Universal block-comment markdown

By default, `semiliterate` scans for block-comment markdown `/** md` ... `**/`
in all files with _any_ extension, as it's valid in so many disparate languages.
(As opposed to `simple`, which defaults to searching for such markdown in a
specific list of file types.)
    """

    super_sdict = dict(SimplePlugin.config_scheme)
    super_semi_dflt = super_sdict['semiliterate'].default
    semi_dflt = [b if 'js' not in b['pattern'] else dict(b, pattern=r'\.')
                 for b in super_semi_dflt]
    altered_config_scheme = dict(
        super_sdict,
        semiliterate=config_options.Type(list, default=semi_dflt)).items()

    add_param_doc = r""" md
### Additional plugin parameters

`semiliterate` adds a couple of new plugin parameters to further tailor its
behavior as compared to `simple`. They are described in this section, with
default values in parentheses at the beginning of each entry.

{! plugin.py extract:
  start: '[*]altered_config_scheme'
  replace:
  - ["\\('(.*)',\\s*$", '\1\n']
  - ['config_options.Type.*?default=([^\)]*)', ':  (\1)']
  - '^\s*#(.*\s*)$'
terminate: '^\s*\)'
!}
    """
    config_scheme = (
        # Note documentation of each new parameter **follows** the parameter.
        *altered_config_scheme,
        ('exclude_extensions',
         config_options.Type(list, default=['.o'])),
        #    Files whose name contains a string in this list will not be
        #    processed by `semiliterate`, regardless of whether they might
        #    match `include_extensions`, the `semiliterate` patterns, or
        #    standard Markdown.
        ('copy_standard_markdown',
         config_options.Type(bool, default=False)),
        #    Whether to add MkDocs' list of standard Markdown extensions to
        #    the `include_extensions` parameter so that Markdown files will be
        #    directly copied to the docsite. Note that the `simple` behavior
        #    corresponds to a _true_ value for `copy_standard_markdown`, but
        #    `semiliterate` still incorporates all standard Markdown files
        #    because of the following `extract_standard_markdown` parameter.
        ('extract_standard_markdown',
         config_options.Type(dict, default={})),
        #    If the `enable` key of this dict parameter is true
        #    (it defaults to the opposite of `copy_standard_markdown`),
        #    it adds a semiliterate block causing extraction (and hence
        #    include-directive processing) from all standard Markdown files
        #    (as defined by MkDocs). The remaining keys of this parameter are
        #    included as parameters of that semiliterate block. Thus, the
        #    default values of the parameters arrange for Markdown files to be
        #    copied "as-is", except possibly for embedded inclusions.
        #    On the other hand, setting this parameter to `{enable: false}`
        #    (which is also the default when `copy_standard_markdown` is true)
        #    will prevent automatic extraction (and hence disable
        #    inclusion-directive processing) from standard Markdown files.
        ('extract_on_copy',
         config_options.Type(bool, default=False)),
        #    Whether to also attempt extraction from a file that is copied
        #    verbatim (because of matching the `include_extensions`).
    )

    def on_config(self, config, **kwargs):
        # Since we have extensions in Demiliterate, suppress the semiliterate
        # configuration until we handle it ourselves:
        semi = self.config['semiliterate']
        self.config['semiliterate'] = []
        new_config = super().on_config(config, **kwargs)
        self.config['semiliterate'] = semi
        self.semiliterate = [Demiliterate(**item) for item in semi]
        self.exclude_extensions = self.config['exclude_extensions']
        dflt_enable = False
        if not self.config['copy_standard_markdown']:
            self.include_extensions = self.config['include_extensions']
            dflt_enable = True
        if self.config['extract_standard_markdown'].get('enable', dflt_enable):
            ext_pat = '|'.join(re.escape(s) for s in utils.markdown_extensions)
            self.semiliterate.append(
                Demiliterate(
                    pattern=re.compile(f"^(.*(?:{ext_pat}))$"),
                    destination=r'\1',
                    **self.config['extract_standard_markdown']))
        return new_config

    def in_extensions(self, file):
        if any(ext in file for ext in self.exclude_extensions):
            return False
        return super().in_extensions(file)

    def extract_from(self, from_directory, name, to_directory):
        if any(ext in name for ext in self.exclude_extensions):
            return False
        if not self.config['extract_on_copy'] and self.in_extensions(name):
            return False
        return super().extract_from(from_directory, name, to_directory)


class Demiliterate(Semiliterate):
    r""" md  Extends Semiliterate to use StreamInclusion, not StreamExtract

semiliterate.ensurelines
:   (true) Guarantees that a newline is trancribed for each line of the input,
    even if a start, stop, terminate, or replacement pattern would have
    suppressed the newline. Note this can be set separately for each block
    (i.e. filename pattern) within the semiliterate parameter. The default
    setting corresponds to the `simple` behavior, so setting this to "false"
    allows you to suppress newlines with judicious use of these patterns.
    """

    def __init__(
            self,
            pattern,
            destination=None,
            terminate=None,
            ensurelines=True,
            extract=[]):
        super().__init__(pattern, destination, terminate)
        self.ensure_lines = ensurelines
        if isinstance(extract, dict):
            extract = [extract]
        self.patterns = [FlextractionPattern(**p) for p in extract]
        if len(self.patterns) == 0:
            self.patterns = [FlextractionPattern()]

    # Note this needs to be identical to Semiliterate.try_extraction
    # except with StreamInclusion in place of StreamExtract in the
    # `extraction =` line, and a couple of options as noted below:
    def try_extraction(
            self,
            from_directory,
            from_file,
            destination_directory,
            **kwargs):
        """Try to extract documentation from file with name.

        Returns True if extraction was successful.
        """
        to_file = self.filenname_match(from_file)
        if not to_file:
            return False
        from_file_path = os.path.join(from_directory, from_file)
        try:
            with open(from_file_path) as original_file:
                utils.log.debug(f"mkdocs-semiliterate: Scanning {from_file}...")
                # extraction = StreamExtract(
                extraction = StreamInclusion(
                    input_stream=original_file,
                    output_stream=LazyFile(destination_directory, to_file),
                    include_root=from_directory,  # ## ADDED
                    ensurelines=self.ensure_lines,  # ## ADDED
                    terminate=self.terminate,
                    patterns=self.patterns,
                    **kwargs)
                return extraction.extract()
        except BaseException as error:
            utils.log.error(
                f"mkdocs-semiliterate: could not build {from_file_path}:\n  "
                + str(error))
        return False

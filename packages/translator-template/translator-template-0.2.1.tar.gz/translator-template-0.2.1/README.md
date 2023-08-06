# translator-template
Generate a Word Document Template for Translator

## Prerequisite

* python 3.7 or greater
* poetry

Download the dependent modules by running `poetry install`

## Running the code

```
poetry run generate --in-file {input-text-file} --out-file {output-docx-file}
```

If the `--out-file` argument is omitted, the `--in-file` argument value is used, with the extension replaced with `.docx`.

## Input Format Specification

In regular expression form the input is the following:

`^((\d|\*\d+\*)-?)*$`

For a given page, the number of panels is represented either by a single digit if the count of panels is fewer than 10.  When the count of panels is greater than or equal to 9, the count is sandwiched between a pair of asterisks.

The panel count can be optionally followed by a hyphen.  This signifies that the panels span two pages.

## Output Specification

The output is a Word DOCX file.  This contains three paragraph styles:

* PagePara
* PanelPara
* QuotePara

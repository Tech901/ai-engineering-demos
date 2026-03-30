# Fonts

## Klingon pIqaD HaSta

This directory contains the Klingon pIqaD HaSta font, which is used to display Klingon text in the traditional pIqaD script.

**Font:** Klingon pIqaD HaSta  
**Designer:** Mike Neff (qa'vaj), modified by Michael Everson  
**License:** SIL Open Font License 1.1  
**Source:** https://www.evertype.com/fonts/tlh/

### License

This font is licensed under the SIL Open Font License, Version 1.1. See `pIqaD-HaSta-licence.txt` for the full license text.

The font is freely available for use in this project and can be bundled, embedded, and redistributed with the software.

### Usage

The font is automatically applied to translations in the Klingon pIqaD script (language code: `tlh-Piqd`) via CSS:

```css
.translation-item[data-lang="tlh-Piqd"] .translation-text {
    font-family: 'Klingon pIqaD', sans-serif;
    font-size: 24px;
    line-height: 1.8;
}
```

### Credits

- Original design: Mike Neff (qa'vaj)
- Font modifications: Michael Everson (Evertype)
- Encoding: ConScript Unicode Registry (CSUR) for Klingon pIqaD

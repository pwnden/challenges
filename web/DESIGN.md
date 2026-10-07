---
name: pwnden challenge targets
description: Shared presentation for the seven Vue challenge target sites.
colors:
  background: "#101722"
  foreground: "#dae4f2"
  surface: "#182334"
  divider: "#34455c"
  control-border: "#6489ad"
  accent: "#94c5ff"
  link-hover: "#c0ddff"
  button: "#263b54"
  button-hover: "#314c69"
  button-pressed: "#1c3048"
  error: "#ffb7b7"
typography:
  body:
    fontFamily: "'Pretendard Variable', sans-serif"
    fontSize: "16px"
    lineHeight: 1.65
  title:
    fontFamily: "'Pretendard Variable', sans-serif"
    fontSize: "1.5rem"
    lineHeight: 1.35
  section-heading:
    fontFamily: "'Pretendard Variable', sans-serif"
    fontSize: "1.1rem"
  code:
    fontFamily: "'D2Coding', monospace"
rounded:
  control: "0.5rem"
spacing:
  inset: "1rem"
  control-inset: "calc((2.75rem - 1.5rem - 2px) / 2)"
---

# Design System: challenge targets

## Overview

The seven target sites share a dark blue canvas, readable Korean text and simple document sections. Their site titles and content identify the individual challenge. [style.css](src/style.css) and [TargetPage.vue](src/TargetPage.vue) own the shared presentation.

## Colors

The background and foreground tokens set the document palette. The surface supports inputs and document output; dividers separate headers, sections and table rows. Accent marks links, input carets and keyboard focus. Buttons use their resting, hover and pressed colors. Errors use the error token with readable feedback text.

## Typography

Pretendard Variable and D2Coding are bundled locally and load with `font-display: optional`. Body text, controls and document output share Pretendard; titles and section headings use the recorded scales. Explicit `code` elements use D2Coding through `--font-code`, including SQL and JSON blocks. Document output preserves whitespace, wraps long text and allows scrolling. Critical fonts are preloaded from the document head. If a font arrives too late, the page retains its fallback face rather than replacing already visible text.

## Layout

The main document is centered with a maximum width of (52rem). Main, header, sections, table cells and document output use equal four-sided inset padding. The header wraps its title and home link with an inset-sized gap.

Standard forms place a labeled field beside its action and stack at (28rem). Login forms use one column with a maximum width of (26rem). Fields and buttons share a height of (2.75rem), a content line height of (1.5rem) and equal four-sided padding calculated from height, line height and border thickness.

## Shapes

Controls and document output share the rounded control shape. Thin borders frame controls and separate content sections.

## Components

`TargetPage` provides one page heading and a home link on inner pages. HTML responses include inert JSON with the current page data and HTTP status, so full-document navigation and history restoration render ready content without a second request. The entry module blocks rendering until the synchronous mount completes. Internal page navigation retains the current content while requesting the destination data, then replaces the page with ready content. Network failures retain the current page and display an alert; HTTP errors render the destination's error state. Native browser history owns back and forward navigation. Raw documents and downloads retain ordinary browser navigation. Standalone development without server-supplied page data retains the initial loading status.

Forms use visible labels and native inputs. Links navigate through ordinary anchors; search and document lookup use normal GET forms with named query fields. Login submits JSON, disables its button while pending and reserves a feedback line. The user-role form saves the browser cookie and reloads the page.

The workshop shop groups balance, product offers and order history in separate sections. Product cards wrap into one column when space is limited. Each order shows its original price, actual payment, refund and status together. Buying and cancelling update server-supplied state and share a reserved feedback line. A receipt appears beside its completed order. Refresh recovers current state after an uncertain request; reset starts a new attempt for the current account.

Vue text interpolation displays server content, queries, policy JSON, filenames and document bodies as escaped text. Search results use a semantic table with column headings. Lists of notes, files and revisions use semantic lists and links. All interactive elements receive the shared visible keyboard focus outline. Fonts and built assets are served locally.

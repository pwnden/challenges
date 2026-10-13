---
name: pwnden challenge targets
description: Shared presentation for the nine Vue challenge target sites.
colors:
  background: "#f6f6f3"
  surface: "#ffffff"
  tint: "#eceae4"
  foreground: "#1f1f1c"
  muted: "#55554f"
  divider: "#d4d4cc"
  control-border: "#8c8c84"
  accent: "#1c5db3"
  accent-hover: "#154a91"
  accent-pressed: "#0f3a73"
  danger: "#a3201a"
  danger-tint: "#fdecea"
  success: "#1d6b47"
  success-tint: "#e7f3ec"
typography:
  body:
    fontFamily: "'Pretendard Variable', sans-serif"
    fontSize: "16px"
    lineHeight: 1.65
  title:
    fontFamily: "'Pretendard Variable', sans-serif"
    fontSize: "1.35rem"
    lineHeight: 1.35
  section-heading:
    fontFamily: "'Pretendard Variable', sans-serif"
    fontSize: "1.15rem"
  code:
    fontFamily: "'D2Coding', monospace"
rounded:
  control: "0.4rem"
spacing:
  inset: "1rem"
  control-height: "2.75rem"
---

# Design system: challenge targets

## Overview

The nine target sites share one light design system in [style.css](src/style.css), built on a few shared parts in `src/`: [TargetPage.vue](src/TargetPage.vue) (loading, errors and the page frame), [SiteHeader.vue](src/SiteHeader.vue), [Field.vue](src/Field.vue), [SubmitButton.vue](src/SubmitButton.vue), [Toaster.vue](src/Toaster.vue), the [useAction](src/useAction.ts) helper and [sectile.ts](src/sectile.ts), the one module that exposes sectile to scenario files. A site keeps its own file small: structure, its texts, and styles that only it needs. Site names and content identify the individual challenge; sites do not carry explanatory disclaimers such as footers about being a practice site.

`TargetPage` always draws the header, so a page that fails to load or is refused still shows its name and links. A site adds its page links and account actions through the `nav` and `actions` slots and puts everything else in the default slot.

## Colors

Tokens are CSS variables on `:root`: `--bg` and `--paper` for the page and its surfaces, `--tint` for table headers and chips, `--ink` and `--muted` for text, `--line` and `--line-strong` for dividers and control borders, one blue `--accent` with its darker states, and `--danger` and `--success` with their tints. Text pairs are measured at 4.5:1 or better (muted text 6.9:1 on the page, white on the accent 6.4:1, toast text 5.7:1 or better). Links use the accent. Errors use `--danger` text with a text message, never color alone.

## Typography

Pretendard Variable and D2Coding are bundled locally and load with `font-display: optional`. Body text, controls and output share Pretendard; `code` uses D2Coding through `--font-code`. Korean text breaks at word boundaries and long identifiers wrap. Critical fonts are preloaded from the document head; a font that arrives late does not replace visible text.

## Layout

The main column is centered at 62rem with a one-rem inset. A `section` is a bordered surface (`section.plain` removes the surface); cards reuse the same look. Forms place a labeled field beside its action and stack at 28rem. Fields and buttons share a height of 2.75rem (small buttons 2.25rem). Tables sit in a `.scroll` region that scrolls on its own, so the page never scrolls sideways at 320px.

## Components

Buttons are neutral by default; `primary` is the accent, `danger` an outlined red, and `small` the compact size. Inputs and text areas come from sectile's `TextField` through `Field`, which supplies the label. Forms that submit through script use sectile's `FormRoot` and `SubmitButton`; forms that navigate with a GET stay native. Progress uses sectile's progress parts, styled by each site from the `--sectile-progress-percentage` variable.

Outcomes appear as toasts from `Toaster.vue`, built on sectile's toast parts. A toast is a zero-height sticky region placed right after the page header, so it sits below the header with its balance and links and stays pinned to the top of the viewport while the page scrolls. Errors are red and stay seven seconds, confirmations are green and stay four, both announce themselves, close with a button or Escape, and keep the latest three. Only changes the user needs to notice get a toast: errors, purchases, cancellations, registrations and resets, not every lookup or star.

## Sites

The workshop shop has two pages with their own addresses: the products at `/` and the order history at `/orders`. Both share a top bar with the store name, links to the two pages (the current one marked with `aria-current`) and the buyer account with its balance and the refresh and reset buttons. After a purchase the toast links to the order page. The product page lists the weekly coupon, the cancellation rule and the receipt rule as labeled rows, then product cards with the name, price, description and the coupon field beside the buy button, with a text label on the coupon target; the cards wrap into one column when space is limited. The order page is a table so the original price, actual payment and refund of every order can be compared in columns, with a bordered receipt for the limited item below it.

The support desk groups the current account, its own inquiries, the staff invitation and the staff page in sections. An inquiry or the staff confirmation opens in a card below its form; the card clears when the next request starts.

The star run groups the track rules, the current run and the record board in sections. The current run shows the stars picked so far with a progress bar and a button that stays disabled until the next star is available. The record code is an editable text area with its submit button, and the board is a semantic table that highlights the player's row. The trophy appears in a card only when the server returns it.

The memo site (`note-vault`) is a small notes app: a centered login card, then the signed-in account's notes as a list of rows with their numbers, and each note on its own page with a link back to the list. The header shows the signed-in account as a chip, and a wrong password appears as a toast.

The document site (`paper-session`) has two pages, the working notes and the recovery key, linked from the header, with the role the server decided shown as a chip. The cookie experiment is its own section with the editable role field.

The parcel box (`path-parcel`) puts a file-name search above a list of files and a viewer; the open file is marked in the list and the viewer says how to open one when none is open. The member search (`query-desk`) is a search field, the condition the search used in a code block, and a results table with an empty row when nothing matches. The web archive (`forgotten-shelf`) has a collections page of tiles and an operations page, linked from the header. The team document site (`borrowed-badge`) lists its documents in a table with the links each one allows and an open-by-name field, then the account's access rules as formatted JSON and the function names, and its history and version pages as lists and a document card.

All six keep their server requests, links and texts; text from the server, queries, policy JSON, filenames and document bodies is displayed as escaped text. Search results and document lists use semantic tables inside a scrolling region, and lists of notes, files and revisions use semantic lists and links. All interactive elements receive the shared visible focus outline. Fonts and built assets are served locally.

# Writing conventions

- Write all posts and page text (`post.md`, and the `title`, `subTitle` and `summary` in `page.json`) in British English: colour, neighbourhood, recognise, optimising, serialised, authorisation, modelling, grey.
- Leave code, identifiers, JSON keys and CSS names as they are (`color`, `colorScheme`, `navbarColor`), and keep quoted text and proper names as written.
- When adding or editing a post, check it for American spellings before finishing.

# Previewing

- Gerard checks changes in the Netlify preview of the branch, so there is no need to ask for or arrange a local preview. Run `vados check --source root --img-source imgroot` before finishing, and say what to look at in the preview (for example that a YouTube embed plays).
- Never commit the generated `public/` folder; it is git-ignored and Netlify builds it.
- Don't add a local dev server or preview script (the old `serve.py` was removed on purpose). If a one-off local check is needed, put any helper in the session's scratchpad directory, not in the repo.

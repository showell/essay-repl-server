# The book's early-draft deploy: ready when you are

*Prepared in its own lane by one agent and merged to master. Nothing has touched staging or prod. No hurry: this waits behind the book.*

## What's in place

- **Stable page names.** Every published chapter's page name comes from an explicit table (`Book.slugs`), not its heading, so a retitle can't move a URL. The build stops on a missing slug, a duplicate, or a stale one.

  | Chapter | Page |
  |---|---|
  | Introduction | introduction.html |
  | The problem | the-problem.html |
  | Platforms, packages and modules | platforms-packages-and-modules.html |
  | The pieces as types | the-pieces-as-types.html |
  | Things | things.html |
  | **Billboard Critters** | **billboard-critters.html** |
  | Shapes | shapes.html |

- **A thin bar at the top of every page**, with "This is an early draft." on the left and "roc-apps on GitHub" on the right.
- **Only the reviewed chapters** get published, set by `PUBLISHED_CHAPTERS` (7 today). The checker found no link to an unpublished page.
- **`site/publish.sh tutorial`** publishes the book. It refuses if a published page would vanish, or if a widget in staging differs from the dev build.

Preview: **http://143.244.172.148:9210/draft/billboard-critters.html**

## The commands, when you're ready

```text
nice -n 19 shale canvas_apps/safari/gates/publish.shale
for w in safari frame_widget route_widget cow_widget herd_widget bend_animals_widget shapes_widget; do site/publish.sh $w; done
site/publish.sh tutorial
# look at http://143.244.172.148:9200/tutorial/ , then:
site/deploy.sh
```

The first step takes about 6 minutes. The URLs will be `https://roc.lynrummy.com/tutorial/billboard-critters.html` and so on. To roll back, `git revert` the publish commits and redeploy. `publish.sh safari` also replaces the live Safari app with today's build, which includes dusk.

## Your decisions

1. **The folder name.** It's `tutorial/` today, and it's in every URL from now on, so settle it before the first deploy. `safari-book/` is the obvious alternative.
2. **A link from the landing page** ("Safari Ride, the book (an early draft)", on the Safari card): keep it or drop it. It only goes live through `site/publish.sh home`.
3. **A way back to the site:** add the "Steve's Roc Apps" pill that every app page has?
4. **Wording:** "This is an early draft." and "roc-apps on GitHub".

# The Conifer table: two drafts

*Both explain the `Conifer` module in "Nature types". They come right after the paragraph you approved ("`Conifer` is a nominal type. …"). Each has one brief sentence before it, and one after it for what fits no row.*

## Draft A: syntax-first

*This is the table in the book now, with the adversarial reviewer's fixes. Every row is one piece of the code. `scenery_height` gets its place, the two ways of calling become rows, and "method" is defined here once (chapter 10's second introduction of it goes).*

The table reads the module's code, piece by piece:

| Syntax | Purpose | Explanation |
|---|---|---|
| `Conifer :=` | Identity | It declares `Conifer` as a nominal type. |
| `[Green, SmallGreen, Red, Gold]` | Variants | The backing type: the four tags a `Conifer` can be. |
| `.{` and `}` | Methods | The braces hold `Conifer`'s methods, `scenery_height` and `scenery_sprite`. A method is a function inside a type's braces. A nominal type can carry methods because it's a type of its own, and the next chapter shows why that matters. |
| `conifer.scenery_height()` | Calling | A method call: the value, a dot, then the method. `scenery_sprite` calls it to hand the tree's height to `TreeShapes.tree_sprite`, the function that drew the far tree. |
| `Green \| SmallGreen =>` | Grouping | One branch for two tags, because both greens share a color. |
| `is_eq : _` | Equality | It asks the compiler for `==`, as it did for `Distance`, and here `==` compares tags. |
| `foliage_color(conifer)` | Privacy | A plain call to a helper outside the braces. Definitions outside the braces stay private to the module. |

A module's definitions can come in any order, so the methods use values defined below them.

## Draft B: concept-driven

*This one follows your original instructions. Every row is a Roc concept, named in plain words, and its explanation points at the code that shows it. The Purpose words form one set, as chapter 2's challenges do.*

The module's code shows these Roc concepts:

| Concept | Purpose | Explanation |
|---|---|---|
| A nominal type | Identity | `Conifer :=` gives `Conifer` a name of its own. Roc keeps it apart from every other type, even another union of the same four tags. |
| A tag union | Variants | The backing type, `[Green, SmallGreen, Red, Gold]`, lists every sort of tree a `Conifer` can be, and the list is fixed. |
| Methods | Behavior | Functions inside the type's braces: `scenery_height` and `scenery_sprite`. A value calls one with a dot, as in `conifer.scenery_height()`. The next chapter shows why they sit inside the braces. |
| Privacy | Hiding | Everything outside the braces stays private to the module: the heights, the colors and `foliage_color`. A call names a private function plainly: `foliage_color(conifer)`. |
| One branch, two tags | Grouping | In a `match`, `Green \| SmallGreen =>` gives both greens one color. |
| Equality | Comparison | `is_eq : _` asks the compiler to write `==`, as it did for `Distance`, and here `==` compares tags. |

`scenery_sprite` hands the height and the color to `TreeShapes.tree_sprite`, the function that drew the far tree. A module's definitions can come in any order, so the methods use values defined below them.

## How they differ

- **A follows the code's own order,** so a reader can scan the module and the table together. Its first column is code, and the Purpose word says what that code is for.
- **B follows the ideas,** so a reader takes away six Roc concepts by name. Its first column is plain words, and the code moves into the explanations.
- **Same content:** both cover the same six ideas, so the choice is about what the reader holds onto, the syntax or the concept.

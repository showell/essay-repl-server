# gopher-roc: the design in pictures

Drawn from the code by `tools/diagram.shale`; never edited by hand.

## Modules and what they import

```dot
digraph modules {
  rankdir=LR;
  node [shape=box, style=rounded, fontname="sans-serif"];
  "Ascii";
  "Author" -> "Ascii";
  "Author";
  "Conversation" -> "Message";
  "Conversation" -> "Topic";
  "Conversation";
  "ConversationSpec" -> "Conversation";
  "ConversationSpec" -> "Message";
  "ConversationSpec" -> "Sample";
  "ConversationSpec";
  "md.Md" [shape=box3d];
  "Html" -> "md.Md";
  "Html" -> "Timestamp";
  "Html";
  "Message" -> "Author";
  "Message" -> "Timestamp";
  "Message" -> "Topic";
  "Message";
  "Page" -> "Conversation";
  "Page" -> "Html";
  "Page" -> "Message";
  "Page" -> "Topic";
  "Page";
  "PageSpec" -> "Conversation";
  "PageSpec" -> "Page";
  "PageSpec" -> "Sample";
  "PageSpec";
  "Sample" -> "Author";
  "Sample" -> "Conversation";
  "Sample" -> "Message";
  "Sample" -> "Timestamp";
  "Sample" -> "Topic";
  "Sample";
  "Separator";
  "Specs" -> "ConversationSpec";
  "Specs" -> "PageSpec";
  "Specs" -> "TranscriptSpec";
  "Specs";
  "Timestamp" -> "Ascii";
  "Timestamp";
  "Topic" -> "Ascii";
  "Topic";
  "Transcript" -> "Author";
  "Transcript" -> "Conversation";
  "Transcript" -> "Message";
  "Transcript" -> "Separator";
  "Transcript" -> "Timestamp";
  "Transcript" -> "Topic";
  "Transcript";
  "TranscriptSpec" -> "Conversation";
  "TranscriptSpec" -> "Sample";
  "TranscriptSpec" -> "Transcript";
  "TranscriptSpec";
}
```

## Types, by module

A bold box is opaque (`::`); a plain one nominal (`:=`). An arrow: the type's definition names the other.

```dot
digraph types {
  rankdir=LR;
  compound=true;
  node [shape=box, fontname="sans-serif"];
  subgraph "cluster_Ascii" {
    label="Ascii.roc";
    style=rounded;
    "Ascii" [label="Ascii ::", shape=box, style=bold];
  }
  subgraph "cluster_Author" {
    label="Author.roc";
    style=rounded;
    "Author" [label="Author ::", shape=box, style=bold];
  }
  subgraph "cluster_Conversation" {
    label="Conversation.roc";
    style=rounded;
    "Conversation" [label="Conversation ::", shape=box, style=bold];
  }
  subgraph "cluster_ConversationSpec" {
    label="ConversationSpec.roc";
    style=rounded;
    "ConversationSpec" [label="ConversationSpec ::", shape=box, style=bold];
  }
  subgraph "cluster_Html" {
    label="Html.roc";
    style=rounded;
    "Html" [label="Html ::", shape=box, style=bold];
  }
  subgraph "cluster_Message" {
    label="Message.roc";
    style=rounded;
    "Message" [label="Message ::", shape=box, style=bold];
    "Message.Id" [label="Id ::", shape=box, style=bold];
  }
  subgraph "cluster_Page" {
    label="Page.roc";
    style=rounded;
    "Page" [label="Page ::", shape=box, style=bold];
  }
  subgraph "cluster_PageSpec" {
    label="PageSpec.roc";
    style=rounded;
    "PageSpec" [label="PageSpec ::", shape=box, style=bold];
  }
  subgraph "cluster_Sample" {
    label="Sample.roc";
    style=rounded;
    "Sample" [label="Sample ::", shape=box, style=bold];
  }
  subgraph "cluster_Separator" {
    label="Separator.roc";
    style=rounded;
    "Separator" [label="Separator ::", shape=box, style=bold];
  }
  subgraph "cluster_Specs" {
    label="Specs.roc";
    style=rounded;
    "Specs" [label="Specs ::", shape=box, style=bold];
  }
  subgraph "cluster_Timestamp" {
    label="Timestamp.roc";
    style=rounded;
    "Timestamp" [label="Timestamp ::", shape=box, style=bold];
  }
  subgraph "cluster_Topic" {
    label="Topic.roc";
    style=rounded;
    "Topic" [label="Topic ::", shape=box, style=bold];
  }
  subgraph "cluster_Transcript" {
    label="Transcript.roc";
    style=rounded;
    "Transcript" [label="Transcript ::", shape=box, style=bold];
  }
  subgraph "cluster_TranscriptSpec" {
    label="TranscriptSpec.roc";
    style=rounded;
    "TranscriptSpec" [label="TranscriptSpec ::", shape=box, style=bold];
  }
  "Conversation" -> "Message";
  "Conversation" -> "Message.Id";
  "Conversation" -> "Topic";
}
```

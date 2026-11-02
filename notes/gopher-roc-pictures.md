# gopher-roc: the design in pictures

Drawn from the code by `tools/diagram.shale`; never edited by hand.

## Modules and what they import

```dot
digraph modules {
  rankdir=LR;
  node [shape=box, style=rounded, fontname="sans-serif"];
  "Author";
  "md.Md" [shape=box3d];
  "Conversation" -> "md.Md";
  "Conversation" -> "Html";
  "Conversation" -> "Message";
  "Conversation" -> "Sample";
  "Conversation" -> "Topic";
  "Conversation" -> "Transcript";
  "Conversation";
  "Html";
  "Message" -> "Author";
  "Message" -> "Timestamp";
  "Message";
  "Sample" -> "Author";
  "Sample" -> "Message";
  "Sample" -> "Timestamp";
  "Sample" -> "Topic";
  "Sample";
  "Timestamp";
  "Topic";
  "Transcript" -> "Author";
  "Transcript" -> "Message";
  "Transcript" -> "Sample";
  "Transcript" -> "Timestamp";
  "Transcript" -> "Topic";
  "Transcript";
}
```

## Types, by module

A bold box is opaque (`::`); a plain one nominal (`:=`). An arrow: the type's definition names the other.

```dot
digraph types {
  rankdir=LR;
  compound=true;
  node [shape=box, fontname="sans-serif"];
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
  subgraph "cluster_Sample" {
    label="Sample.roc";
    style=rounded;
    "Sample" [label="Sample ::", shape=box, style=bold];
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
    "Transcript" [label="Transcript :=", shape=box];
  }
  "Conversation" -> "Message";
  "Conversation" -> "Topic";
  "Message" -> "Author";
  "Message" -> "Message.Id";
  "Message" -> "Timestamp";
}
```

# gopher-roc: the design in pictures

Drawn from the code by `tools/diagram.shale`; never edited by hand.

## Modules and what they import

```dot
digraph modules {
  rankdir=LR;
  node [shape=box, style=rounded, fontname="sans-serif"];
  "Admin" -> "UserId";
  "Admin";
  "Ascii";
  "Author" -> "Name";
  "Author";
  "ChannelName" -> "Name";
  "ChannelName" -> "StrictName";
  "ChannelName";
  "Conversation" -> "Message";
  "Conversation" -> "Topic";
  "Conversation";
  "ConversationSpec" -> "Conversation";
  "ConversationSpec" -> "Message";
  "ConversationSpec" -> "Sample";
  "ConversationSpec";
  "DateTime" -> "Ascii";
  "DateTime";
  "Directory" -> "Admin";
  "Directory" -> "Author";
  "Directory" -> "ChannelName";
  "Directory" -> "Name";
  "Directory" -> "UserId";
  "Directory" -> "UserStem";
  "Directory";
  "DirectorySpec" -> "Admin";
  "DirectorySpec" -> "ChannelName";
  "DirectorySpec" -> "Directory";
  "DirectorySpec" -> "Sample";
  "DirectorySpec" -> "UserId";
  "DirectorySpec";
  "Dm" -> "Conversation";
  "Dm" -> "DateTime";
  "Dm" -> "Directory";
  "Dm" -> "Topic";
  "Dm" -> "UserId";
  "Dm";
  "DmSpec" -> "ChannelName";
  "DmSpec" -> "Directory";
  "DmSpec" -> "DateTime";
  "DmSpec" -> "Dm";
  "DmSpec" -> "Message";
  "DmSpec" -> "Place";
  "DmSpec" -> "Sample";
  "DmSpec" -> "UserId";
  "DmSpec";
  "Escape" -> "TrustedHtml";
  "Escape";
  "HtmlElement" -> "Ascii";
  "HtmlElement" -> "DateTime";
  "HtmlElement" -> "TrustedHtml";
  "HtmlElement";
  "md.Md" [shape=box3d];
  "Markdown" -> "md.Md";
  "Markdown" -> "SecureImageTag";
  "Markdown" -> "TrustedHtml";
  "Markdown";
  "Message" -> "Author";
  "Message" -> "DateTime";
  "Message";
  "Name" -> "NameAlphabet";
  "Name" -> "StrictName";
  "Name";
  "NameAlphabet" -> "Ascii";
  "NameAlphabet";
  "Page" -> "Conversation";
  "Page" -> "HtmlElement";
  "Page" -> "Escape";
  "Page" -> "Markdown";
  "Page" -> "Message";
  "Page" -> "TrustedHtml";
  "Page";
  "PageSpec" -> "Conversation";
  "PageSpec" -> "Page";
  "PageSpec" -> "Sample";
  "PageSpec";
  "Place" -> "ChannelName";
  "Place" -> "Dm";
  "Place";
  "Sample" -> "Author";
  "Sample" -> "Conversation";
  "Sample" -> "Directory";
  "Sample" -> "Message";
  "Sample" -> "DateTime";
  "Sample" -> "Name";
  "Sample" -> "Topic";
  "Sample" -> "UserId";
  "Sample";
  "SecureImageTag";
  "SecureImageTagSpec" -> "Markdown";
  "SecureImageTagSpec";
  "Separator";
  "Specs" -> "ConversationSpec";
  "Specs" -> "DirectorySpec";
  "Specs" -> "DmSpec";
  "Specs" -> "PageSpec";
  "Specs" -> "SecureImageTagSpec";
  "Specs" -> "TranscriptSpec";
  "Specs";
  "StrictName" -> "Ascii";
  "StrictName";
  "Topic" -> "StrictName";
  "Topic";
  "Transcript" -> "Author";
  "Transcript" -> "Conversation";
  "Transcript" -> "Message";
  "Transcript" -> "Separator";
  "Transcript" -> "DateTime";
  "Transcript" -> "Topic";
  "Transcript";
  "TranscriptSpec" -> "Conversation";
  "TranscriptSpec" -> "Message";
  "TranscriptSpec" -> "Sample";
  "TranscriptSpec" -> "Transcript";
  "TranscriptSpec";
  "TrustedHtml";
  "UnvalidatedString" -> "Conversation";
  "UnvalidatedString" -> "DateTime";
  "UnvalidatedString" -> "Name";
  "UnvalidatedString" -> "Topic";
  "UnvalidatedString" -> "Transcript";
  "UnvalidatedString";
  "UserId";
  "UserStem" -> "Ascii";
  "UserStem" -> "Name";
  "UserStem" -> "UserId";
  "UserStem";
}
```

## Types, by module

A bold box is opaque (`::`); a plain one nominal (`:=`). An arrow: the type's definition names the other.

```dot
digraph types {
  rankdir=LR;
  compound=true;
  node [shape=box, fontname="sans-serif"];
  subgraph "cluster_Admin" {
    label="Admin.roc";
    style=rounded;
    "Admin" [label="Admin ::", shape=box, style=bold];
  }
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
  subgraph "cluster_ChannelName" {
    label="ChannelName.roc";
    style=rounded;
    "ChannelName" [label="ChannelName ::", shape=box, style=bold];
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
  subgraph "cluster_DateTime" {
    label="DateTime.roc";
    style=rounded;
    "DateTime" [label="DateTime ::", shape=box, style=bold];
  }
  subgraph "cluster_Directory" {
    label="Directory.roc";
    style=rounded;
    "Directory" [label="Directory ::", shape=box, style=bold];
    "Directory.User" [label="User ::", shape=box, style=bold];
    "Directory.Channel" [label="Channel ::", shape=box, style=bold];
  }
  subgraph "cluster_DirectorySpec" {
    label="DirectorySpec.roc";
    style=rounded;
    "DirectorySpec" [label="DirectorySpec ::", shape=box, style=bold];
  }
  subgraph "cluster_Dm" {
    label="Dm.roc";
    style=rounded;
    "Dm" [label="Dm ::", shape=box, style=bold];
  }
  subgraph "cluster_DmSpec" {
    label="DmSpec.roc";
    style=rounded;
    "DmSpec" [label="DmSpec ::", shape=box, style=bold];
  }
  subgraph "cluster_Escape" {
    label="Escape.roc";
    style=rounded;
    "Escape" [label="Escape ::", shape=box, style=bold];
  }
  subgraph "cluster_HtmlElement" {
    label="HtmlElement.roc";
    style=rounded;
    "HtmlElement" [label="HtmlElement ::", shape=box, style=bold];
    "HtmlElement.Token" [label="Token ::", shape=box, style=bold];
  }
  subgraph "cluster_Markdown" {
    label="Markdown.roc";
    style=rounded;
    "Markdown" [label="Markdown ::", shape=box, style=bold];
  }
  subgraph "cluster_Message" {
    label="Message.roc";
    style=rounded;
    "Message" [label="Message ::", shape=box, style=bold];
    "Message.Id" [label="Id ::", shape=box, style=bold];
  }
  subgraph "cluster_Name" {
    label="Name.roc";
    style=rounded;
    "Name" [label="Name ::", shape=box, style=bold];
    "Name.Key" [label="Key ::", shape=box, style=bold];
  }
  subgraph "cluster_NameAlphabet" {
    label="NameAlphabet.roc";
    style=rounded;
    "NameAlphabet" [label="NameAlphabet ::", shape=box, style=bold];
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
  subgraph "cluster_Place" {
    label="Place.roc";
    style=rounded;
    "Place" [label="Place :=", shape=box];
  }
  subgraph "cluster_Sample" {
    label="Sample.roc";
    style=rounded;
    "Sample" [label="Sample ::", shape=box, style=bold];
  }
  subgraph "cluster_SecureImageTag" {
    label="SecureImageTag.roc";
    style=rounded;
    "SecureImageTag" [label="SecureImageTag ::", shape=box, style=bold];
  }
  subgraph "cluster_SecureImageTagSpec" {
    label="SecureImageTagSpec.roc";
    style=rounded;
    "SecureImageTagSpec" [label="SecureImageTagSpec ::", shape=box, style=bold];
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
  subgraph "cluster_StrictName" {
    label="StrictName.roc";
    style=rounded;
    "StrictName" [label="StrictName ::", shape=box, style=bold];
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
  subgraph "cluster_TrustedHtml" {
    label="TrustedHtml.roc";
    style=rounded;
    "TrustedHtml" [label="TrustedHtml ::", shape=box, style=bold];
  }
  subgraph "cluster_UnvalidatedString" {
    label="UnvalidatedString.roc";
    style=rounded;
    "UnvalidatedString" [label="UnvalidatedString ::", shape=box, style=bold];
  }
  subgraph "cluster_UserId" {
    label="UserId.roc";
    style=rounded;
    "UserId" [label="UserId ::", shape=box, style=bold];
  }
  subgraph "cluster_UserStem" {
    label="UserStem.roc";
    style=rounded;
    "UserStem" [label="UserStem ::", shape=box, style=bold];
  }
  "Admin" -> "UserId";
  "Author" -> "Name";
  "ChannelName" -> "Name";
  "ChannelName" -> "StrictName";
  "Conversation" -> "Message";
  "Conversation" -> "Topic";
  "Directory" -> "Directory.User";
  "Directory" -> "Directory.Channel";
  "Directory" -> "Name";
  "Directory" -> "Name.Key";
  "Directory.User" -> "Directory";
  "Directory.User" -> "Name";
  "Directory.User" -> "UserId";
  "Directory.Channel" -> "ChannelName";
  "Directory.Channel" -> "Name";
  "Directory.Channel" -> "UserId";
  "Dm" -> "UserId";
  "Message" -> "Author";
  "Message" -> "DateTime";
  "Message" -> "Message.Id";
  "Place" -> "ChannelName";
  "Place" -> "Dm";
  "Place" -> "Name";
  "Topic" -> "Name";
  "Topic" -> "StrictName";
}
```

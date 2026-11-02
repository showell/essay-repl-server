# gopher-roc: the design in pictures

Drawn from the code by `tools/diagram.shale`; never edited by hand.

## Modules and what they import

```dot
digraph modules {
  rankdir=LR;
  node [shape=box, style=rounded, fontname="sans-serif"];
  "Admin" -> "SignedIn";
  "Admin" -> "UserId";
  "Admin";
  "AdminSpec" -> "Admin";
  "AdminSpec" -> "Sample";
  "AdminSpec" -> "SignedIn";
  "AdminSpec";
  "Ascii";
  "Author" -> "Name";
  "Author";
  "ChannelName" -> "Name";
  "ChannelName" -> "StrictName";
  "ChannelName";
  "Channels" -> "Admin";
  "Channels" -> "ChannelName";
  "Channels" -> "UserId";
  "Channels" -> "Users";
  "Channels";
  "ChannelsSpec" -> "Admin";
  "ChannelsSpec" -> "ChannelName";
  "ChannelsSpec" -> "Channels";
  "ChannelsSpec" -> "Sample";
  "ChannelsSpec" -> "UserId";
  "ChannelsSpec" -> "Users";
  "ChannelsSpec";
  "Conversation" -> "Author";
  "Conversation" -> "Message";
  "Conversation" -> "MsgAnchor";
  "Conversation" -> "Topic";
  "Conversation";
  "ConversationSpec" -> "Author";
  "ConversationSpec" -> "Conversation";
  "ConversationSpec" -> "Message";
  "ConversationSpec" -> "Sample";
  "ConversationSpec";
  "DateTime" -> "Ascii";
  "DateTime";
  "Directory" -> "Admin";
  "Directory" -> "ChannelName";
  "Directory" -> "Channels";
  "Directory" -> "Name";
  "Directory" -> "Users";
  "Directory";
  "DirectorySpec" -> "Admin";
  "DirectorySpec" -> "ChannelName";
  "DirectorySpec" -> "Directory";
  "DirectorySpec" -> "Sample";
  "DirectorySpec" -> "UserId";
  "DirectorySpec" -> "Users";
  "DirectorySpec";
  "Dm" -> "Conversation";
  "Dm" -> "Message";
  "Dm" -> "Topic";
  "Dm" -> "UserId";
  "Dm" -> "UserPair";
  "Dm" -> "Users";
  "Dm";
  "DmSpec" -> "ChannelName";
  "DmSpec" -> "DateTime";
  "DmSpec" -> "Dm";
  "DmSpec" -> "Message";
  "DmSpec" -> "Sample";
  "DmSpec" -> "UserId";
  "DmSpec" -> "Users";
  "DmSpec";
  "Escape" -> "TrustedHtml";
  "Escape";
  "Html" -> "Ascii";
  "Html" -> "DateTime";
  "Html" -> "TrustedHtml";
  "Html";
  "md.Md" [shape=box3d];
  "Markdown" -> "md.Md";
  "Markdown" -> "SecureImageTag";
  "Markdown" -> "TrustedHtml";
  "Markdown";
  "Message" -> "Author";
  "Message" -> "DateTime";
  "Message";
  "MsgAnchor" -> "Message";
  "MsgAnchor" -> "Topic";
  "MsgAnchor";
  "Name" -> "NameAlphabet";
  "Name" -> "StrictName";
  "Name";
  "NameAlphabet" -> "Ascii";
  "NameAlphabet" -> "StrictName";
  "NameAlphabet";
  "Page" -> "Conversation";
  "Page" -> "Escape";
  "Page" -> "Html";
  "Page" -> "Markdown";
  "Page" -> "Message";
  "Page" -> "MsgAnchor";
  "Page" -> "Topic";
  "Page" -> "TrustedHtml";
  "Page";
  "PageSpec" -> "Conversation";
  "PageSpec" -> "Page";
  "PageSpec" -> "Sample";
  "PageSpec";
  "Place" -> "ChannelName";
  "Place" -> "Channels";
  "Place" -> "Dm";
  "Place" -> "UserPair";
  "Place";
  "PlaceSpec" -> "ChannelName";
  "PlaceSpec" -> "Channels";
  "PlaceSpec" -> "Dm";
  "PlaceSpec" -> "Place";
  "PlaceSpec" -> "Sample";
  "PlaceSpec";
  "Sample" -> "Admin";
  "Sample" -> "Author";
  "Sample" -> "Conversation";
  "Sample" -> "Directory";
  "Sample" -> "Message";
  "Sample" -> "DateTime";
  "Sample" -> "Name";
  "Sample" -> "SignedIn";
  "Sample" -> "Topic";
  "Sample" -> "UserId";
  "Sample" -> "Users";
  "Sample";
  "SecureImageTag";
  "SecureImageTagSpec" -> "Markdown";
  "SecureImageTagSpec";
  "Separator";
  "SignedIn" -> "Name";
  "SignedIn" -> "Users";
  "SignedIn";
  "Specs" -> "AdminSpec";
  "Specs" -> "ChannelsSpec";
  "Specs" -> "ConversationSpec";
  "Specs" -> "DirectorySpec";
  "Specs" -> "DmSpec";
  "Specs" -> "PageSpec";
  "Specs" -> "PlaceSpec";
  "Specs" -> "SecureImageTagSpec";
  "Specs" -> "TranscriptSpec";
  "Specs" -> "UsersSpec";
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
  "TranscriptSpec" -> "Author";
  "TranscriptSpec" -> "Conversation";
  "TranscriptSpec" -> "Message";
  "TranscriptSpec" -> "Sample";
  "TranscriptSpec" -> "Transcript";
  "TranscriptSpec";
  "TrustedHtml";
  "UnvalidatedString" -> "ChannelName";
  "UnvalidatedString" -> "Conversation";
  "UnvalidatedString" -> "DateTime";
  "UnvalidatedString" -> "Name";
  "UnvalidatedString" -> "Topic";
  "UnvalidatedString" -> "Transcript";
  "UnvalidatedString" -> "UserId";
  "UnvalidatedString" -> "UserPair";
  "UnvalidatedString";
  "UserId" -> "Ascii";
  "UserId";
  "UserPair" -> "UserId";
  "UserPair";
  "UserStem" -> "Name";
  "UserStem" -> "NameAlphabet";
  "UserStem" -> "UserId";
  "UserStem";
  "Users" -> "Author";
  "Users" -> "Name";
  "Users" -> "UserId";
  "Users" -> "UserStem";
  "Users";
  "UsersSpec" -> "Sample";
  "UsersSpec" -> "UserId";
  "UsersSpec" -> "Users";
  "UsersSpec";
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
  subgraph "cluster_AdminSpec" {
    label="AdminSpec.roc";
    style=rounded;
    "AdminSpec" [label="AdminSpec ::", shape=box, style=bold];
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
  subgraph "cluster_Channels" {
    label="Channels.roc";
    style=rounded;
    "Channels" [label="Channels ::", shape=box, style=bold];
    "Channels.Channel" [label="Channel ::", shape=box, style=bold];
  }
  subgraph "cluster_ChannelsSpec" {
    label="ChannelsSpec.roc";
    style=rounded;
    "ChannelsSpec" [label="ChannelsSpec ::", shape=box, style=bold];
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
  subgraph "cluster_Html" {
    label="Html.roc";
    style=rounded;
    "Html" [label="Html ::", shape=box, style=bold];
    "Html.Token" [label="Token ::", shape=box, style=bold];
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
  subgraph "cluster_MsgAnchor" {
    label="MsgAnchor.roc";
    style=rounded;
    "MsgAnchor" [label="MsgAnchor ::", shape=box, style=bold];
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
    "NameAlphabet.Written" [label="Written ::", shape=box, style=bold];
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
    "Place" [label="Place ::", shape=box, style=bold];
  }
  subgraph "cluster_PlaceSpec" {
    label="PlaceSpec.roc";
    style=rounded;
    "PlaceSpec" [label="PlaceSpec ::", shape=box, style=bold];
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
  subgraph "cluster_SignedIn" {
    label="SignedIn.roc";
    style=rounded;
    "SignedIn" [label="SignedIn ::", shape=box, style=bold];
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
  subgraph "cluster_UserPair" {
    label="UserPair.roc";
    style=rounded;
    "UserPair" [label="UserPair ::", shape=box, style=bold];
  }
  subgraph "cluster_UserStem" {
    label="UserStem.roc";
    style=rounded;
    "UserStem" [label="UserStem ::", shape=box, style=bold];
  }
  subgraph "cluster_Users" {
    label="Users.roc";
    style=rounded;
    "Users" [label="Users ::", shape=box, style=bold];
    "Users.User" [label="User ::", shape=box, style=bold];
    "Users.Human" [label="Human ::", shape=box, style=bold];
  }
  subgraph "cluster_UsersSpec" {
    label="UsersSpec.roc";
    style=rounded;
    "UsersSpec" [label="UsersSpec ::", shape=box, style=bold];
  }
  "Admin" -> "SignedIn";
  "Author" -> "Name";
  "ChannelName" -> "Name";
  "ChannelName" -> "StrictName";
  "Channels" -> "Channels.Channel";
  "Channels.Channel" -> "ChannelName";
  "Channels.Channel" -> "Name";
  "Channels.Channel" -> "UserId";
  "Conversation" -> "Message";
  "Conversation" -> "Topic";
  "Directory" -> "Channels";
  "Directory" -> "Name";
  "Directory" -> "Name.Key";
  "Directory" -> "Users";
  "Dm" -> "UserPair";
  "Message" -> "Author";
  "Message" -> "DateTime";
  "Message" -> "Message.Id";
  "MsgAnchor" -> "Message";
  "MsgAnchor" -> "Message.Id";
  "MsgAnchor" -> "Topic";
  "Name" -> "NameAlphabet";
  "Name" -> "NameAlphabet.Written";
  "Place" -> "ChannelName";
  "Place" -> "Dm";
  "Place" -> "Name";
  "Place" -> "UserPair";
  "SignedIn" -> "Users";
  "SignedIn" -> "Users.User";
  "Topic" -> "Name";
  "Topic" -> "StrictName";
  "UserPair" -> "UserId";
  "Users" -> "Users.User";
  "Users.User" -> "Name";
  "Users.User" -> "UserId";
  "Users.User" -> "Users";
  "Users.Human" -> "Users";
  "Users.Human" -> "Users.User";
}
```

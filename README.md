# Turingfy - Proof of concept

Ever thought of Spotify playlist's as Turing Machines?

Imagine the songs in your favorite playlist become the symbols on a tape, and the order of those songs becomes a series of instructions. In this intriguing concept, each song in the playlist represents a unique symbol or instruction that the Turingfy Interpreter reads and processes.

Just like a traditional Turing Machine, this musical variant would have a tape, a head that scans the symbols (Playlist's description), and a set of rules (Songs) dictating how to interpret and manipulate the symbols. As the playlist plays, the "head" moves through the songs, following the rules encoded in the playlist, and executing operations accordingly.

By carefully crafting the sequence of songs, one can think of playlist as programs that that solves specific problems, all while **enjoying a curated musical experience.**

## Example Set of Instructions

https://open.spotify.com/playlist/59UpsSIbeT9j7lKDiTy7aT?si=41eacf416f4248a2

## Program Example n1: Binary Palindrome Checker

https://open.spotify.com/playlist/1TGnAeGRWCVZsYxdBPjStO?si=cd10444be59f478d

## Spotify API

Write a `set-env.sh` file with:

```bash
export SPOTIPY_CLIENT_ID=<YOUR SPOTIPY_CLIENT_ID>
export SPOTIPY_CLIENT_SECRET=<YOUR SPOTIPY_CLIENT_SECRET>
export SPOTIPY_REDIRECT_URI=<YOUR SPOTIPY_REDIRECT_URI>
```

Execute

```console
$ source set-env.sh
```

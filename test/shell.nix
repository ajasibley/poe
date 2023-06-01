{ pkgs ? import <nixpkgs> {
    config = { allowUnfree = true; };
  }
}:

pkgs.mkShell {
  buildInputs = with pkgs; [
    just
    cargo
    tree
    poetry
    natscli
    nats-server
    ipfs
    babashka
    ngrok
  ];
  shellHook = ''
    cat <<'EOF'
.-.    n=69 *  *  *    *         * * *
 `-'     *  *      *  *  *        *   *
  __ * *._* *_: * * *:*  *:*.*   *   * *
 . ́ * *`*. * *.:  * * *  *::. .-*
 : * * *:*     *  :* * * *  *:'*
.'* * * * ~:* *.:*`*(*)*`-.:' *
_____________________
  |  _______________  |
  | | *  *  *  *  * | |
  |_|___________________|
 |   | |               |
 |___| |_             _|
|   |_|   |     o    | |
|     |   | [][]-O-|[]|
|_____|___|__(_)__ (_)|___
|   o   _|_  |  .  |  _|
|      (___)_|(___)_| (_)
|_o__o_o__o_o__o_o__o_o__
|  .   .   .   .   .  | .
|_|_|_|_|_|_|___|_|_|_|___|
 |   .   .   .   .   |
_|___|___|___|___|___|____
o o o o o o o o o o o o o
    EOF

    echo "gm gm ⟁"
  '';
}

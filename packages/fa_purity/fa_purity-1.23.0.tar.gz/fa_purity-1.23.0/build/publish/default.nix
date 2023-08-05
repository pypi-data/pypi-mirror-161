{nixpkgs}:
nixpkgs.mkShell {
  packages = with nixpkgs; [
    git
    python310Packages.flit
  ];
}

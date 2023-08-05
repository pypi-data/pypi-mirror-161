lib: nixpkgs: selected_python: let
  python_pkgs = nixpkgs."${selected_python}Packages";
in
  python_pkgs
  // {
    import-linter = import ./import-linter {
      inherit lib;
      click = python_pkgs.click;
      networkx = python_pkgs.networkx;
    };
    types-deprecated = import ./deprecated/stubs.nix lib;
    types-simplejson = import ./simplejson/stubs.nix lib;
  }

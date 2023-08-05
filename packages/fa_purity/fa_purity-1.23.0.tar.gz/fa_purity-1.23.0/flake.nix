{
  description = "Pure functional and typing utilities";
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs";
    nix_filter.url = "github:numtide/nix-filter";
  };
  outputs = {
    self,
    nixpkgs,
    nix_filter,
  }: let
    system = "x86_64-linux";
    metadata = (builtins.fromTOML (builtins.readFile ./pyproject.toml)).project;
    path_filter = nix_filter.outputs.lib;
    src = path_filter {
      root = self;
      include = [
        "mypy.ini"
        "arch.cfg"
        "arch_test.cfg"
        "pyproject.toml"
        (path_filter.inDirectory metadata.name)
        (path_filter.inDirectory "tests")
      ];
    };
    out = import ./. {
      inherit src;
      nixpkgs = nixpkgs.legacyPackages."${system}";
    };
  in {
    packages."${system}" = out;
    defaultPackage."${system}" = self.packages."${system}".python39.pkg;
  };
}

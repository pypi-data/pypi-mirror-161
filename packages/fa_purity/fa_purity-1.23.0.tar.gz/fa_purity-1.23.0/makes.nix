# https://github.com/fluidattacks/makes
{
  cache = {
    readAndWrite = {
      enable = true;
      name = "fa-foss";
      pubKey = "fa-foss.cachix.org-1:RoFAjJdHUUFrNAfbaLFqvFQVfmNmyMMAorl7j2VqV9M=";
    };
  };
  formatBash = {
    enable = true;
    targets = ["/"];
  };
  formatNix = {
    enable = true;
    targets = ["/"];
  };
  formatPython = {
    enable = true;
    targets = ["/"];
  };
  lintBash = {
    enable = true;
    targets = ["/"];
  };
  lintNix = {
    enable = true;
    targets = ["/"];
  };
}

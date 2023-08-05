lib:
lib.buildPythonPackage rec {
  pname = "types-Deprecated";
  version = "1.2.5";
  src = lib.fetchPypi {
    inherit pname version;
    hash = "sha256:0zi858hibpszcpxjxbs4sny280w5rbwav6dmy6gaxm8fm18347vg";
  };
}

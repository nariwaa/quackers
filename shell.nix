{ pkgs ? import <nixpkgs> {} }:

let
  pythonPackages = pkgs.python312Packages;
  pythonWithPackages = pythonPackages.python.withPackages (ps: with ps; [
    aiohappyeyeballs
    aiohttp
    aiosignal
    annotated-types
    anyio
    attrs
    certifi
    charset-normalizer
    distro
    frozenlist
    h11
    httpcore
    httpx
    idna
    jiter
    multidict
    nextcord
    openai
    pillow
    propcache
    pydantic
    pydantic-core
    requests
    sniffio
    tqdm
    typing-extensions
    unidecode
    urllib3
    yarl
  ]);
in
pkgs.mkShell {
  buildInputs = [
    pythonWithPackages
    pythonPackages.pip
  ];

  shellHook = ''
    echo "Python environment ready"
  '';
}

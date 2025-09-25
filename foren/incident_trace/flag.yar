rule flag {
  strings:
    $a = /NCLPS1\{[^\}]{0,256}/ ascii wide
  condition:
    $a
}

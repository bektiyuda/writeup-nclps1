rule all_strings {
  strings:
    $s = /[ -~]{6,}/ ascii wide
  condition:
    $s
}

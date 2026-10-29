{ pkgs ?  import <nixpkgs> {}
, firmware ? import ../src {}
}:

let
  config = ./.;

  # go60-config: per-key LED presets. go60-build writes led_presets.h (from led-presets.json, via go60-leds);
  # the patch adds one lighting effect per preset after MoErgo's four. Without the header, the build is stock.
  ledPresets = drv:
    if builtins.pathExists ./led_presets.h then drv.overrideAttrs (old: {
      patches = (old.patches or []) ++ [ ./patches/rgb-presets.patch ];
      postPatch = (old.postPatch or "") + ''
        cp ${./led_presets.h} src/led_presets.h
      '';
    }) else drv;

  go60_left  = ledPresets (firmware.zmk.override { board = "go60_lh"; keymap = "${config}/go60.keymap"; kconfig = "${config}/go60.conf"; });
  go60_right = ledPresets (firmware.zmk.override { board = "go60_rh"; keymap = "${config}/go60.keymap"; kconfig = "${config}/go60.conf"; });

in firmware.combine_uf2 go60_left go60_right "go60"

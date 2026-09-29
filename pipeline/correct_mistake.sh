#!/usr/bin/env bash

# correction script for JVS dataset
# - performs listed renames and removals only if the source exists
# - prints actions; use --apply to actually execute
# - default: dry-run

set -u

APPLY=0
if [[ "${1:-}" == "--apply" ]]; then
  APPLY=1
fi

safe_mv() {
  local src="$1" dst="$2"
  if [[ -e "$src" ]]; then
    if [[ -e "$dst" ]]; then
      echo "Moving and overwriting: $src -> $dst"
      if [[ "$APPLY" -eq 1 ]]; then
        mv -f -- "$src" "$dst"
      fi
    else
      echo "Moving: $src -> $dst"
      if [[ "$APPLY" -eq 1 ]]; then
        mv -- "$src" "$dst"
      fi
    fi
  else
    echo "Source missing, skipping mv: $src"
  fi
}

safe_rm() {
  local f="$1"
  if [[ -e "$f" ]]; then
    echo "Removing: $f"
    if [[ "$APPLY" -eq 1 ]]; then
      rm -- "$f"
    fi
  else
    echo "Missing, skipping rm: $f"
  fi
}

# renames (apply in order)
declare -a MOVES=(
  "jvs_ver1/jvs058/parallel100/wav24kHz16bit/VOICEACTRESS100_021.wav|jvs_ver1/jvs058/parallel100/wav24kHz16bit/VOICEACTRESS100_022.wav"
  "jvs_ver1/jvs058/parallel100/wav24kHz16bit/VOICEACTRESS100_020.wav|jvs_ver1/jvs058/parallel100/wav24kHz16bit/VOICEACTRESS100_021.wav"
  "jvs_ver1/jvs058/parallel100/wav24kHz16bit/VOICEACTRESS100_019.wav|jvs_ver1/jvs058/parallel100/wav24kHz16bit/VOICEACTRESS100_020.wav"
  "jvs_ver1/jvs058/parallel100/wav24kHz16bit/VOICEACTRESS100_018.wav|jvs_ver1/jvs058/parallel100/wav24kHz16bit/VOICEACTRESS100_019.wav"
  "jvs_ver1/jvs058/parallel100/wav24kHz16bit/VOICEACTRESS100_017.wav|jvs_ver1/jvs058/parallel100/wav24kHz16bit/VOICEACTRESS100_018.wav"
  "jvs_ver1/jvs058/parallel100/wav24kHz16bit/VOICEACTRESS100_016.wav|jvs_ver1/jvs058/parallel100/wav24kHz16bit/VOICEACTRESS100_017.wav"
  "jvs_ver1/jvs058/parallel100/wav24kHz16bit/VOICEACTRESS100_015.wav|jvs_ver1/jvs058/parallel100/wav24kHz16bit/VOICEACTRESS100_016.wav"
)

echo "== MOVES =="
for entry in "${MOVES[@]}"; do
  IFS='|' read -r src dst <<< "$entry"
  safe_mv "$src" "$dst"
done

# removals: misreadings (including subtle ones such as ルィ→リ) + recording errors (e.g., truncations)
declare -a REMOVES=(
  "jvs_ver1/jvs001/parallel100/wav24kHz16bit/VOICEACTRESS100_085.wav"
  "jvs_ver1/jvs001/parallel100/wav24kHz16bit/VOICEACTRESS100_100.wav"
  "jvs_ver1/jvs003/parallel100/wav24kHz16bit/VOICEACTRESS100_100.wav"
  "jvs_ver1/jvs004/parallel100/wav24kHz16bit/VOICEACTRESS100_045.wav"
  "jvs_ver1/jvs004/parallel100/wav24kHz16bit/VOICEACTRESS100_084.wav"
  "jvs_ver1/jvs004/parallel100/wav24kHz16bit/VOICEACTRESS100_100.wav"
  "jvs_ver1/jvs005/parallel100/wav24kHz16bit/VOICEACTRESS100_005.wav"
  "jvs_ver1/jvs005/parallel100/wav24kHz16bit/VOICEACTRESS100_019.wav"
  "jvs_ver1/jvs005/parallel100/wav24kHz16bit/VOICEACTRESS100_021.wav"
  "jvs_ver1/jvs006/parallel100/wav24kHz16bit/VOICEACTRESS100_084.wav"
  "jvs_ver1/jvs007/parallel100/wav24kHz16bit/VOICEACTRESS100_019.wav"
  "jvs_ver1/jvs009/parallel100/wav24kHz16bit/VOICEACTRESS100_056.wav"
  "jvs_ver1/jvs009/parallel100/wav24kHz16bit/VOICEACTRESS100_068.wav"
  "jvs_ver1/jvs009/parallel100/wav24kHz16bit/VOICEACTRESS100_076.wav"
  "jvs_ver1/jvs011/parallel100/wav24kHz16bit/VOICEACTRESS100_006.wav"
  "jvs_ver1/jvs011/parallel100/wav24kHz16bit/VOICEACTRESS100_084.wav"
  "jvs_ver1/jvs012/parallel100/wav24kHz16bit/VOICEACTRESS100_028.wav"
  "jvs_ver1/jvs015/parallel100/wav24kHz16bit/VOICEACTRESS100_085.wav"
  "jvs_ver1/jvs019/parallel100/wav24kHz16bit/VOICEACTRESS100_019.wav"
  "jvs_ver1/jvs020/parallel100/wav24kHz16bit/VOICEACTRESS100_085.wav"
  "jvs_ver1/jvs021/parallel100/wav24kHz16bit/VOICEACTRESS100_065.wav"
  "jvs_ver1/jvs022/parallel100/wav24kHz16bit/VOICEACTRESS100_068.wav"
  "jvs_ver1/jvs023/parallel100/wav24kHz16bit/VOICEACTRESS100_045.wav"
  "jvs_ver1/jvs024/parallel100/wav24kHz16bit/VOICEACTRESS100_021.wav"
  "jvs_ver1/jvs024/parallel100/wav24kHz16bit/VOICEACTRESS100_085.wav"
  "jvs_ver1/jvs032/parallel100/wav24kHz16bit/VOICEACTRESS100_017.wav"
  "jvs_ver1/jvs035/parallel100/wav24kHz16bit/VOICEACTRESS100_085.wav"
  "jvs_ver1/jvs043/parallel100/wav24kHz16bit/VOICEACTRESS100_047.wav"
  "jvs_ver1/jvs053/parallel100/wav24kHz16bit/VOICEACTRESS100_087.wav"
  "jvs_ver1/jvs054/parallel100/wav24kHz16bit/VOICEACTRESS100_018.wav"
  "jvs_ver1/jvs055/parallel100/wav24kHz16bit/VOICEACTRESS100_090.wav"
  "jvs_ver1/jvs056/parallel100/wav24kHz16bit/VOICEACTRESS100_076.wav"
  "jvs_ver1/jvs058/parallel100/wav24kHz16bit/VOICEACTRESS100_076.wav"
  "jvs_ver1/jvs059/parallel100/wav24kHz16bit/VOICEACTRESS100_065.wav"
  "jvs_ver1/jvs060/parallel100/wav24kHz16bit/VOICEACTRESS100_085.wav"
  "jvs_ver1/jvs062/parallel100/wav24kHz16bit/VOICEACTRESS100_085.wav"
  "jvs_ver1/jvs070/parallel100/wav24kHz16bit/VOICEACTRESS100_090.wav"
  "jvs_ver1/jvs073/parallel100/wav24kHz16bit/VOICEACTRESS100_078.wav"
  "jvs_ver1/jvs074/parallel100/wav24kHz16bit/VOICEACTRESS100_035.wav"
  "jvs_ver1/jvs088/parallel100/wav24kHz16bit/VOICEACTRESS100_022.wav"
  "jvs_ver1/jvs090/parallel100/wav24kHz16bit/VOICEACTRESS100_021.wav"
  "jvs_ver1/jvs095/parallel100/wav24kHz16bit/VOICEACTRESS100_078.wav"
  "jvs_ver1/jvs096/parallel100/wav24kHz16bit/VOICEACTRESS100_092.wav"
  "jvs_ver1/jvs097/parallel100/wav24kHz16bit/VOICEACTRESS100_084.wav"
  "jvs_ver1/jvs097/parallel100/wav24kHz16bit/VOICEACTRESS100_087.wav"
  "jvs_ver1/jvs009/parallel100/wav24kHz16bit/VOICEACTRESS100_086.wav"
  "jvs_ver1/jvs009/parallel100/wav24kHz16bit/VOICEACTRESS100_095.wav"
  "jvs_ver1/jvs017/parallel100/wav24kHz16bit/VOICEACTRESS100_082.wav"
  "jvs_ver1/jvs018/parallel100/wav24kHz16bit/VOICEACTRESS100_072.wav"
  "jvs_ver1/jvs022/parallel100/wav24kHz16bit/VOICEACTRESS100_047.wav"
  "jvs_ver1/jvs024/parallel100/wav24kHz16bit/VOICEACTRESS100_088.wav"
  "jvs_ver1/jvs036/parallel100/wav24kHz16bit/VOICEACTRESS100_057.wav"
  "jvs_ver1/jvs037/parallel100/wav24kHz16bit/VOICEACTRESS100_086.wav"
  "jvs_ver1/jvs038/parallel100/wav24kHz16bit/VOICEACTRESS100_006.wav"
  "jvs_ver1/jvs038/parallel100/wav24kHz16bit/VOICEACTRESS100_041.wav"
  "jvs_ver1/jvs043/parallel100/wav24kHz16bit/VOICEACTRESS100_085.wav"
  "jvs_ver1/jvs047/parallel100/wav24kHz16bit/VOICEACTRESS100_085.wav"
  "jvs_ver1/jvs048/parallel100/wav24kHz16bit/VOICEACTRESS100_043.wav"
  "jvs_ver1/jvs048/parallel100/wav24kHz16bit/VOICEACTRESS100_076.wav"
  "jvs_ver1/jvs051/parallel100/wav24kHz16bit/VOICEACTRESS100_025.wav"
  "jvs_ver1/jvs055/parallel100/wav24kHz16bit/VOICEACTRESS100_056.wav"
  "jvs_ver1/jvs055/parallel100/wav24kHz16bit/VOICEACTRESS100_076.wav"
  "jvs_ver1/jvs055/parallel100/wav24kHz16bit/VOICEACTRESS100_099.wav"
  "jvs_ver1/jvs058/parallel100/wav24kHz16bit/VOICEACTRESS100_014.wav"
  "jvs_ver1/jvs059/parallel100/wav24kHz16bit/VOICEACTRESS100_061.wav"
  "jvs_ver1/jvs059/parallel100/wav24kHz16bit/VOICEACTRESS100_064.wav"
  "jvs_ver1/jvs059/parallel100/wav24kHz16bit/VOICEACTRESS100_066.wav"
  "jvs_ver1/jvs059/parallel100/wav24kHz16bit/VOICEACTRESS100_074.wav"
  "jvs_ver1/jvs060/parallel100/wav24kHz16bit/VOICEACTRESS100_082.wav"
  "jvs_ver1/jvs074/parallel100/wav24kHz16bit/VOICEACTRESS100_062.wav"
  "jvs_ver1/jvs098/parallel100/wav24kHz16bit/VOICEACTRESS100_060.wav"
  "jvs_ver1/jvs098/parallel100/wav24kHz16bit/VOICEACTRESS100_099.wav"
)

echo "== REMOVALS =="
for f in "${REMOVES[@]}"; do
  safe_rm "$f"
done

if [[ "$APPLY" -eq 0 ]]; then
  echo "Dry-run mode: use --apply to perform actions."
fi

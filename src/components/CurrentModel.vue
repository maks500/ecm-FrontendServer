<template>
  <div>
    <legend>Model Details</legend>
    <h4>Equations</h4>
    <div v-katex:display="equations"></div>
    <div v-if="currentModel.expressions">
      <h4>Where</h4>
      <div v-katex:display="expressions"></div>
      <div v-katex:display="observables"></div>
    </div>
  </div>
</template>

<script>
function spaceLines(latexStr, spacing = 12) {
  return latexStr.replace(/(\\\\)/g, String.raw`$1[${spacing}pt]`);
}

export default {
  computed: {
    equations: function() {
      let out = "";
      if (this.currentModel.equations) {
        out += "\\begin{aligned}";
        this.currentModel.equations.forEach((eq) => {
          out += String.raw`${eq.nameLatex} = &\ ${eq.valueLatex}\\`;
        });
        out += "\\end{aligned}";
      }
      return spaceLines(out);
    },
    expressions: function() {
      let out = "";
      if (this.currentModel.expressions) {
        out += "\\begin{aligned}";
        this.currentModel.expressions.forEach((expr) => {
          out += String.raw`${expr.nameLatex} = &\ ${expr.valueLatex}\\`;
        });
        out += "\\end{aligned}";
      }
      return spaceLines(out);
    },
    observables: function() {
      let out = "";
      if (this.currentModel.observables.length > 0) {
        out += "\\begin{aligned}";
        this.currentModel.observables.forEach((expr) => {
          out += String.raw`${expr.nameLatex} = &\ ${expr.valueLatex}\\`;
        });
        out += "\\end{aligned}";
      }
      return spaceLines(out);
    },
  },
  props: ["currentModel"],
};
</script>

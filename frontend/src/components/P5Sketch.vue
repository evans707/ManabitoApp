<template>
  <div ref="p5Container" class="fixed inset-0 -z-10 bg-white"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import p5 from 'p5';

const p5Container = ref(null);
let sketchInstance = null;

const sketch = (p) => {
  let particles = [];

  p.setup = () => {
    p.createCanvas(p.windowWidth, p.windowHeight).parent(p5Container.value);
    p.noStroke();

    for (let i = 0; i < 150; i++) {
      particles.push({
        pos: p.createVector(p.random(p.width), p.random(p.height)),
        color: p.color(p.random(180, 220), p.random(200, 255), p.random(180, 220), 15)
      });
    }
  };

  p.draw = () => {
    p.background(255, 255, 255, 10);

    particles.forEach(pt => {
      p.fill(pt.color);
      p.circle(pt.pos.x, pt.pos.y, p.random(2, 12));

      pt.pos.add(pt.vel);

      if (pt.pos.x < 0 || pt.pos.x > p.width) pt.vel.x *= -1;
      if (pt.pos.y < 0 || pt.pos.y > p.height) pt.vel.y *= -1;
    });
  };

  p.windowResized = () => {
    p.resizeCanvas(p.windowWidth, p.windowHeight);
  };
};

onMounted(() => {
  sketchInstance = new p5(sketch);
});

onUnmounted(() => {
  sketchInstance.remove();
});
</script>
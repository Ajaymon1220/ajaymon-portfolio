/* Ajaymon's photo-inspired mascot. Replace the two 3×3 PNGs to update the likeness. */
(() => {
  const base = '/profile/mascot/';
  class AjayMascot extends HTMLElement {
    connectedCallback() {
      // Next.js moves streamed nodes into place, causing disconnect/reconnect.
      // Reuse the shadow DOM, but always restore listeners after a disconnect.
      if (this.abort && !this.abort.signal.aborted) return;
      const root = this.shadowRoot || this.attachShadow({mode:'open'});
      if (!this.face) root.innerHTML = `<style>
        :host{display:block;aspect-ratio:1;position:relative;contain:layout style}
        button{display:block;width:100%;height:100%;padding:0;border:0;border-radius:25%;background:transparent;cursor:pointer;touch-action:manipulation;-webkit-tap-highlight-color:transparent}
        button:focus-visible{outline:2px solid var(--accent,#e75636);outline-offset:5px}
        .face{display:block;width:100%;height:100%;background-image:url('${base}directions.png');background-size:300% 300%;background-position:50% 50%;background-repeat:no-repeat;pointer-events:none;filter:drop-shadow(0 3px 2px #00000012)}
        .face.react{background-image:url('${base}reactions.png')}
        .status{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)}
        @media(prefers-reduced-motion:no-preference){button:active{transform:scale(.97)}}
      </style><button type="button" aria-label="Ajaymon’s interactive mascot. Click or tap for an expression." title="Hi, I’m Ajaymon. Tap me!"><span class="face" aria-hidden="true"></span></button><span class="status" role="status" aria-live="polite"></span>`;
      this.face = root.querySelector('.face');
      this.button = root.querySelector('button');
      this.abort = new AbortController();
      const options = {signal:this.abort.signal};
      this.motion = matchMedia('(prefers-reduced-motion: reduce)');
      this.pointer = matchMedia('(any-pointer: fine)');
      this.visible = true;
      this.reaction = false;
      this.frame = 4;
      this.expression = 0;
      this.observer = new IntersectionObserver(entries => {
        this.visible = entries[0].isIntersecting;
        if(!this.visible) this.reset();
      });
      this.observer.observe(this);
      this.button.addEventListener('click', () => this.react(), options);
      window.addEventListener('pointermove', e => {
        if(!this.visible || this.reaction || this.motion.matches || !this.pointer.matches || e.pointerType === 'touch') return;
        this.point = {x:e.clientX,y:e.clientY};
        if(!this.raf) this.raf = requestAnimationFrame(() => {
          this.raf = 0;
          if(!this.point || this.reaction) return;
          const rect = this.getBoundingClientRect();
          const dx = this.point.x - rect.left - rect.width/2;
          const dy = this.point.y - rect.top - rect.height/2;
          if(Math.hypot(dx,dy) < Math.max(24,rect.width*.35)) return this.paint(4);
          const sector = (Math.round(Math.atan2(dy,dx)/(Math.PI/4))+8)%8;
          this.paint([5,8,7,6,3,0,1,2][sector]);
        });
      }, {...options,passive:true,capture:true});
      document.documentElement.addEventListener('pointerleave', () => {if(!this.reaction)this.paint(4)}, options);
      document.addEventListener('visibilitychange', () => {if(document.hidden)this.reset()}, options);
      this.motion.addEventListener('change', () => this.reset(), options);
      // Preload expressions before the first click to avoid flashing a blank frame.
      this.sheet = new Image(); this.sheet.src = base+'reactions.png';
    }
    paint(frame) {
      this.frame = frame;
      this.face.style.backgroundPosition = `${(frame%3)*50}% ${Math.floor(frame/3)*50}%`;
    }
    react() {
      clearTimeout(this.timer);
      this.reaction = true;
      const frames = [0,1,2,3,5,6,7,8];
      const labels = ['Hello!','A little wink.','Oh!','That made me laugh.','Thinking…','You made my day.','Time for a little rest.','Good to see you!'];
      const i = this.expression++ % frames.length;
      this.face.classList.add('react'); this.paint(frames[i]);
      this.shadowRoot.querySelector('.status').textContent = labels[i];
      this.timer = setTimeout(() => this.reset(), this.motion.matches ? 2200 : 1400);
    }
    reset() {
      clearTimeout(this.timer); cancelAnimationFrame(this.raf); this.raf = 0;
      this.reaction = false; this.face?.classList.remove('react');
      if(this.face)this.paint(4);
    }
    disconnectedCallback() {
      this.reset(); this.abort?.abort(); this.observer?.disconnect();
    }
  }
  if(!customElements.get('ajay-mascot'))customElements.define('ajay-mascot',AjayMascot);
})();

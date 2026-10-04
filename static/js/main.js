/* ============================================================
   Quickbyte - main.js
   Image fallbacks, AJAX cart, quantity steppers, nav & flashes.
   ============================================================ */
(function () {
  "use strict";

  const CSRF = document.querySelector('meta[name="csrf-token"]')?.content || "";

  /* -------- helpers -------- */
  function postForm(url, data) {
    const body = new URLSearchParams(data);
    body.set("csrf_token", CSRF);
    return fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": CSRF,
      },
      body,
    }).then((r) => r.json());
  }

  function money(n) {
    n = Number(n) || 0;
    return "₹" + (Number.isInteger(n) ? n : parseFloat(n.toFixed(2)));
  }

  function toast(msg) {
    const t = document.getElementById("toast");
    if (!t) return;
    t.textContent = msg;
    t.classList.add("show");
    clearTimeout(t._timer);
    t._timer = setTimeout(() => t.classList.remove("show"), 2200);
  }

  function setBadge(count) {
    const b = document.getElementById("cartBadge");
    if (!b) return;
    b.textContent = count;
    b.classList.toggle("hidden", !count);
  }

  /* -------- image fallback: pretty local SVG placeholder -------- */
  const PALETTE = [
    ["#FF8A4C", "#FF5A1F"], ["#FFB347", "#FF7A18"], ["#FF6B6B", "#EE5253"],
    ["#54A0FF", "#2E86DE"], ["#1DD1A1", "#10AC84"], ["#A29BFE", "#6C5CE7"],
    ["#FECA57", "#FF9F43"], ["#48DBFB", "#0ABDE3"],
  ];
  function hash(str) {
    let h = 0;
    for (let i = 0; i < str.length; i++) h = (h * 31 + str.charCodeAt(i)) >>> 0;
    return h;
  }
  window.quickbyteImgFallback = function (img) {
    img.onerror = null; // prevent loops
    const emoji = img.dataset.emoji || "🍽️";
    const label = (img.dataset.label || "").slice(0, 22);
    const [c1, c2] = PALETTE[hash(label || emoji) % PALETTE.length];
    const svg =
      `<svg xmlns='http://www.w3.org/2000/svg' width='400' height='300'>` +
      `<defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'>` +
      `<stop offset='0' stop-color='${c1}'/><stop offset='1' stop-color='${c2}'/>` +
      `</linearGradient></defs>` +
      `<rect width='400' height='300' fill='url(#g)'/>` +
      `<text x='200' y='140' font-size='110' text-anchor='middle' dominant-baseline='central'>${emoji}</text>` +
      `<text x='200' y='230' font-size='24' font-family='Segoe UI,Arial' font-weight='700' ` +
      `fill='rgba(255,255,255,.95)' text-anchor='middle'>${label}</text></svg>`;
    img.src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);
  };

  /* -------- run after DOM ready -------- */
  document.addEventListener("DOMContentLoaded", function () {
    /* mobile nav */
    const toggle = document.getElementById("navToggle");
    const links = document.getElementById("navLinks");
    if (toggle && links) {
      toggle.addEventListener("click", () => links.classList.toggle("open"));
    }

    /* dismiss flash messages */
    document.querySelectorAll(".flash").forEach((f) => {
      f.querySelector(".flash-x")?.addEventListener("click", () => f.remove());
      setTimeout(() => f.remove(), 5000);
    });

    /* quantity steppers on food-detail page */
    document.querySelectorAll(".qty-add .qty-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const input = btn.parentElement.querySelector(".qty-input");
        const step = parseInt(btn.dataset.step, 10);
        let v = (parseInt(input.value, 10) || 1) + step;
        v = Math.max(1, Math.min(20, v));
        input.value = v;
      });
    });

    /* add-to-cart forms (AJAX with graceful fallback) */
    document.querySelectorAll(".add-to-cart-form").forEach((form) => {
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        const fd = new FormData(form);
        postForm("/cart/add", {
          food_id: fd.get("food_id"),
          qty: fd.get("qty") || 1,
        })
          .then((res) => {
            if (res.ok) {
              setBadge(res.cart_count);
              toast(res.message || "Added to cart");
            } else {
              toast(res.error || "Could not add item");
            }
          })
          .catch(() => form.submit()); // network issue -> normal POST
      });
    });

    /* cart page interactions */
    initCartPage();
  });

  function initCartPage() {
    const layout = document.getElementById("cartLayout");
    if (!layout) return;

    function applyTotals(cart) {
      setBadge(cart.count);
      const sub = document.getElementById("sumSubtotal");
      const del = document.getElementById("sumDelivery");
      const tot = document.getElementById("sumTotal");
      const note = document.getElementById("freeNote");
      if (sub) sub.textContent = money(cart.subtotal);
      if (del)
        del.innerHTML = cart.delivery_fee
          ? money(cart.delivery_fee)
          : '<span class="free">FREE</span>';
      if (tot) tot.textContent = money(cart.total);
      if (note)
        note.textContent = cart.delivery_fee
          ? "Add " + money(500 - cart.subtotal) + " more for free delivery"
          : "";
      // per-line totals
      Object.entries(cart.lines || {}).forEach(([id, val]) => {
        const el = document.querySelector('.line-total[data-id="' + id + '"]');
        if (el) el.textContent = money(val);
      });
      if (cart.empty) window.location.reload();
    }

    function update(id, qty) {
      postForm("/cart/update", { food_id: id, qty: qty }).then((r) => {
        if (r.ok) applyTotals(r.cart);
      });
    }

    layout.querySelectorAll(".cart-item").forEach((row) => {
      const id = row.dataset.id;
      const valEl = row.querySelector(".qty-val");
      row.querySelector(".cart-inc")?.addEventListener("click", () => {
        const q = (parseInt(valEl.textContent, 10) || 1) + 1;
        valEl.textContent = q;
        update(id, q);
      });
      row.querySelector(".cart-dec")?.addEventListener("click", () => {
        let q = (parseInt(valEl.textContent, 10) || 1) - 1;
        if (q < 1) {
          row.remove();
          update(id, 0);
          return;
        }
        valEl.textContent = q;
        update(id, q);
      });
      row.querySelector(".cart-remove")?.addEventListener("click", () => {
        postForm("/cart/remove", { food_id: id }).then((r) => {
          if (r.ok) {
            row.remove();
            applyTotals(r.cart);
          }
        });
      });
    });
  }
})();

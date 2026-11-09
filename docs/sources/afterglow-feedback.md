# Afterglow: what can come back from the previous frame

Looked at 2026-11-09, after a code review found that a guard promised on the libretro forum (post 24,
2026-10-21) was never written.

## The question

A user with Intel HD 4600 graphics (Haswell, Mesa 26.2.4, RetroArch 1.22.2) got noise around the picture and
purple stripes with `amiga-1084s` on glcore, and a clean picture on Vulkan (forum posts 9 and 20). The
answer in post 24 guessed that the afterglow's feedback buffer started out with garbage, and promised to
discard invalid values from the previous frame. The afterglow lines of `crt.inc` were not changed after
that. Can garbage reach them, and is the guard worth having?

## Source: RetroArch's filter chains (emulator source, read 2026-11-09)

`gfx/drivers_shader/shader_gl3.cpp` at tag v1.22.2:

- A pass with feedback has two framebuffers, `framebuffer` and `framebuffer_feedback`
  (`Pass::init_feedback`). After every frame they are swapped (`Pass::end_frame`).
- Only `framebuffer` is ever sized: `Pass::build_commands` calls `framebuffer->set_size(size)` when the size
  differs. `Framebuffer::init` then makes a new texture with `glTexStorage2D` and does not clear it.
- `clear_history_and_feedback()` runs once, on the first frame after the chain is built (`require_clear`),
  and only for framebuffers that are complete. A new `Framebuffer` has no texture yet, so on that first
  frame the feedback is not cleared; it is read as texture 0.
- The pass then draws a quad over the whole target.

So a target is always drawn in full before it is swapped and read back as feedback, at start and after a
resize. Its texture is not cleared, but none of the old memory is ever read. `shader_vulkan.cpp` at the
same tag has the same structure (`require_clear`, `swap(framebuffer, fb_feedback)`, `set_size` on
`framebuffer` only).

## What was worked out

- **The guess in post 24 does not hold for RetroArch** (inferred from the source above, not tested on that
  GPU): stale memory in the feedback buffer cannot reach the shader on glcore or Vulkan. What caused the
  noise on the HD 4600 is still not known. The user did not report back on Phosphor afterglow 0.
- **The afterglow can still lock a bad value in.** The line is `col = max(col, prev * Phosphor afterglow)`.
  A finite value fades by that factor every frame (0.08 by default: gone in two or three frames). Inf does
  not: Inf times 0.08 is Inf, and the max keeps it. With NaN, `max` may return either argument (the GLSL
  spec leaves it undefined). So one Inf or NaN at a pixel, in any one frame, stays there until the preset is
  loaded again. It could come from a pass's own arithmetic on some driver, or from a frontend other than
  RetroArch that hands over a target it did not clear.
- **The guard.** The previous frame's value is used only if it is 0 or more and below 64; otherwise 0. A
  comparison with NaN is false, so NaN and Inf both fail. Each channel is picked with `?:`, not multiplied
  by a 0/1 mask: NaN times 0 is still NaN. 64 is above anything the pass writes: at most 1 in SDR (after
  the shoulder) plus the room's reflection, and in HDR the peak over paper white, 25 at most (2000 / 80
  nits, the parameters' limits).

## Checked (2026-11-09)

Offscreen on macOS OpenGL 4.1 (M4 Pro), a one-pixel pass with the same lines and the previous frame's value
fed in as raw bits, over a picture value of 0.25: NaN, +Inf, -Inf, -1 and 65 give no afterglow (0.25 comes
out); 0.5, 10 and 63 give what they gave before (0.25, 0.8, 5.04). Without the guard +Inf comes out as Inf
and 65 as 5.2; NaN came out as 0.25 on this GPU (its `max` returned the picture's value).

Not checked: the HD 4600 itself, and frontends other than RetroArch.

## Where the code uses it

- `shaders/lola-retro/shaders/crt.inc`, the afterglow block at the end of `main` (full presets only: the
  lite and super lite presets and the ports have no feedback).

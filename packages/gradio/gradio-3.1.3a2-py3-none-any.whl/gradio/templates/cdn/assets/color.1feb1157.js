import { ae as ordered_colors } from './index.06e6b58c.js';

const get_next_color = (index) => {
  return ordered_colors[index % ordered_colors.length];
};

export { get_next_color as g };

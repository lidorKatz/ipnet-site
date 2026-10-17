// Raw authoring renders are local intermediates, never deployment assets.
import {rm,stat} from "node:fs/promises";
await stat("out/index.html");
await rm("out/journey/raw",{recursive:true,force:true});
console.log("Static export prepared; raw authoring renders excluded.");

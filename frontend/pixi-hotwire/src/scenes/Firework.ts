import { Container, ParticleContainer, Texture } from "pixi.js";
import { Emitter, upgradeConfig } from "@pixi/particle-emitter";
import * as particleConfig from "../fireworks.json";

export class Firework extends Container {
  private particleContainer: ParticleContainer | null = null;
  private emitter: Emitter | null = null;
  private emitCounter: number = 0;

  constructor(root: Container) {
    super();
    this.particleContainer = new ParticleContainer();
    root.addChild(this.particleContainer);
    this.emitter = new Emitter(
      this.particleContainer,
      upgradeConfig(particleConfig, [Texture.from("particle.png")])
    );
    this.emitter.autoUpdate = true;
    this.emitter.updateSpawnPos(400, 400);
    this.emitter.emit = true;
  }

  public update(deltaTime: number): void {
    this.emitCounter += deltaTime;
    if (this.emitter && this.emitCounter > 50) {
      this.emitCounter = 0;
      this.emitter.updateSpawnPos(Math.random() * 600, Math.random() * 600);
      this.emitter.resetPositionTracking();
      this.emitter.emit = true;
    }
  }
}
# Actions #

"Action" is a short piece of code that is called at every frame update to manipulate an "actor" (which are usually sprites) without the programmer having to manage things manually in his own main loop or scene. Actions also help performance, as all the action that need to do something every frame are implemented in C++. There two ways to initiate an action:

```
action.do(sprite)
sprite.do(action)
```

They are basically equivalent, but action.do(sprite) returns a bound Action object and sprite.do(action) returns the sprite object (for method chaining).

The bound action is a copy of the original action, so it is possible to do the following

```
act2 = act1.do(sprite1)
act2.limit(time=2)
```

without affecting the original act1 action.

For actions that do not take any parameters, you can use an instance or the class itself, i.e.

```
sprite.do(Delete)
sprite.do(Delete())
```

are equivalent.

## Action Chaining ##

Actions can be chained so than when an action ends, it automatically triggers another action. For example, to move a sprite left 100 pixels and then delete it, you could write:

```
sprite.do(MoveDelta((100,0), secs=1) + Delete)
```

For two simultaneous actions, you can either call do twice, or use the Fork action.

```
sprite.do(MoveDelta((100,0), secs=1))
sprite.do(AlphaFade(0, secs=1))
# or
sprite.do(MoveDelta((100,0), secs=1)).do(AlphaFade(0, secs=1))
```

Fork is mostly useful when it's in the middle of a longer chain. You can also divide action chains into several temporary variables to make the code more readable.

```
delay = Delay(1)
move = MoveDelta((100,0), secs=1)
move += Delete
fade = AlphaFade(0, secs=1)
sprite.do(delay + Fork(move) + fade)
```

It is also perfectly valid to use the same chain for several actors. I.e.

```
chain = delay + move + delete
sprite1.do(chain)
sprite2.do(chain)
```

## Interval Actions ##

Some actions work linearly over a time interval and have common characteristics. Each such action takes a secs parameter which dictates the number of seconds for one interval. The second common parameter is mode which can be one of StopMode (default), RepeatMode or PingPongMode. StopMode performs the interval once, RepeatMode repeats it over from the beginning and PingPongMode performs every other interval backwards.

Interval actions have a method called smooth(acceleration, deceleration) that can be used to make the action non-linear at the beginning and end so that the action is accelerated and stopped smoothly. The given parameters are the number of seconds from the beginning and end of the interval to smoothen out.
## List of All Actions ##
### Misc. Sprite Management ###

  * Delete(): delete the actor
  * SetAttr(kw=value): set the given attributes in the actor

### Meta Actions / Flow Control ###

  * Fork(`*`actions): start executing all the given actions concurrently for the same actor
  * Repeat(action `[,repeats]`): repeat the given action indefinitely or the given number of times
  * SetActor(sprite): use this to change the actor in the middle of an action chain
  * CallFunc(func, `*`arg, `**`kw): call the given function (or any callable object)
  * SetScene(scene, `*`arg, `**`kw): change the current scene
  * SetState(state, `*`arg, `**`kw): change the current state
  * Delay(seconds): wait for the given amount of seconds before continuing the action chain

### Sprite Movement and Orientation ###

  * Move(velocity): move the actor with velocity (vx,vy)
  * MoveDelta((dx,dy), secs, mode): (interval) move the actor over the given distance
  * MoveTo((x,y), secs, mode): (interval) move the actor to the given destination position
  * Rotate(speed): rotate the actor with the given speed (degrees per second)
  * RotateDelta(delta, secs, mode): (interval) rotate the actor the given amount of degrees
  * RotateTo(direction, secs|speed, mode `[,dir]`): (interval) rotate the actor to the given orientation
  * KeepFacing(sprite, offset=0): keep the actor rotated to face the given other sprite
  * Scale(speed, multiply=True): scale the sprite with the given speed (addition or multiplication per second)
  * ScaleTo(dstscale, secs, mode): (interval) scale the sprite to the given size
  * FollowPath(points, curve, speed, align=True): move the actor through the given path of points

### Sprite Appearance ###

  * AlphaFade(dstalpha, secs, mode): (interval) fade the actor's alpha value to the given destination value
  * ColorFade((r,g,b,a), secs, mode): (interval) fade the actor's color to the given value
  * Animate(frames, secs|fps, mode, `[,start_frame] [,start_direction]`): animate the actor through the given list of images
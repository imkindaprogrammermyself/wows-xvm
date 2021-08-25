package
{
	import lesta.api.ModBase;
	import flash.text.TextField;
	import flash.text.TextFormat;
	import flash.text.TextFieldAutoSize;
	import flash.display.DisplayObject;
	import flash.display.Sprite;
	import mx.utils.StringUtil;
	/**
	 * ...
	 * @author notyourfather
	 */
	public class Main extends ModBase
	{
		private var tfAllyRatings: TextField;
		private var tfEnemyRatings: TextField;
		private var yPosAlly: Number = 120;
		private var yPosEnemy: Number = 120;
		private var displayObjects: Vector.<DisplayObject>;
		private var fontSize: Number = 14;

		public function Main()
		{
			super();
			tfAllyRatings = new TextField();
			tfEnemyRatings = new TextField();
			displayObjects = new Vector.<DisplayObject>();
		}

		override public function init():void
		{
			super.init();
			gameAPI.data.addCallBack("wowsxvm.addPlayer", addPlayer);
			gameAPI.data.addCallBack("wowsxvm.clear", clear);
			gameAPI.data.addCallBack("wowsxvm.showHide", showHide);
		}

		override public function fini():void
		{
			super.fini();
		}

		override public function updateStage(width:Number, height:Number):void
		{
			super.updateStage(width, height);
		}

		public function showHide():void
		{
			displayObjects.forEach(function (dp: DisplayObject):void
			{
				dp.visible = !dp.visible
			});
		}

		public function clear():void
		{
			displayObjects.forEach(function (dp: DisplayObject):void
			{
				gameAPI.stage.removeChild(dp);
			});
			yPosAlly = 120;
			yPosEnemy = 120;
			displayObjects.length = 0;
		}

		public function addPlayer(playerName:String, playerColor: Number, clanName:String, clanColor:Number, ally:Boolean):void
		{
			var tf: TextField = new TextField();
			var formatPr: TextFormat = new TextFormat();
			var bgSprite: Sprite = new Sprite();

			formatPr.color = playerColor;
			formatPr.size = fontSize;
			formatPr.bold = true;

			if (clanName) {
				var formatClan: TextFormat = new TextFormat();

				formatClan.color = clanColor;
				formatClan.size = fontSize;
				formatClan.bold = true;

				var subClanPlayerRating:String = "[{0}]{1}";
				tf.text = StringUtil.substitute(subClanPlayerRating, clanName, playerName);
				tf.setTextFormat(formatClan, 0, clanName.length + 2);
				tf.setTextFormat(formatPr, clanName.length + 2, tf.text.length);
			} else {
				tf.text = playerName;
				tf.setTextFormat(formatPr, 0, playerName.length);
			}

			if (ally == true) {
				tf.autoSize = TextFieldAutoSize.LEFT;
				tf.x = 10;
				tf.y = yPosAlly;
				yPosAlly += tf.height;
			} else {
				tf.autoSize = TextFieldAutoSize.RIGHT;
				tf.x = gameAPI.stage.width - 10 - tf.width;
				tf.y = yPosEnemy;
				yPosEnemy += tf.height;
			}

			bgSprite.graphics.beginFill(0x000000, 0.25);
			bgSprite.graphics.drawRect(tf.x, tf.y, tf.width, tf.height);
			bgSprite.graphics.endFill();

			gameAPI.stage.addChild(bgSprite);
			gameAPI.stage.addChild(tf);
			displayObjects.push(tf);
			displayObjects.push(bgSprite);
		}
	}

}
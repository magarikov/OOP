
// main.cpp — рефакторинг в ООП

#include <GL/freeglut.h>
#include <time.h>
#include <stdio.h>
#include <stb_easy_font.h>   //для выведения букв
#include <stdlib.h>
#include <iostream>
#include <vector>
using namespace std;

// GLOBAL CONST

// звезды - фон
double speed_of_stars = 1.0;

// пули корабля
double speed_of_bullet = -1.5;

// астероиды - то, что уничтожаем
double speed_of_asteroids = 2.0; // коэффицент изменения скорости астероидов
double size_first_asteroid = 7;

// бонусы
double speed_of_bonus = 1;
double size_of_bonus = 0.4;
#define CAN_TAKE_NEW_BONUS 100 // количество тиков, нужное для того, чтобы подобрать новый бонус

// корабль
double size_of_spaceship = 7;
#define REGENIGATION_TIME 2000 // количество тиков, нужное для того, чтобы жизнь могла отняться повторно


// it affects on current screen and game params
int difficulty = 0; // 0 - меню выбора сложности, 1 - easy, 2 - medium, 3 - hard, -1 - меню проигрыша, -2 - pause

void print_string(float x, float y, const char* input_text, float r, float g, float b) //кусок кода, вытащенный из библиотеки сверху, нужен для печати букв
{																	//
	static char buffer[9000]; // ~500 chars
	int num_quads;
	char* print_text = new char[256];
	strcpy_s(print_text, 256, input_text);

	num_quads = stb_easy_font_print(x, y, print_text, NULL, buffer, sizeof(buffer));

	glColor3f(r, g, b);
	glEnableClientState(GL_VERTEX_ARRAY);
	glVertexPointer(2, GL_FLOAT, 16, buffer);
	glDrawArrays(GL_QUADS, 0, num_quads * 4);
	glDisableClientState(GL_VERTEX_ARRAY);

	delete[]print_text;
}

// GAME OBJECTS
class Entity {
public:
	double x, y;
	double speed;
	bool alive = true;

	double object_scale = 1; // размер
	//double speed_coefficient = 1; // коэффициент скорости

	void update() {
		x -= speed;
		if ((x < -110) || (x > 200)) alive = false;
	}

	virtual void draw() const = 0;
	virtual const char* classname() const { return "Entity"; }

};

class Star : public Entity {
public:

	double speed_coefficient = speed_coefficient;

	Star(double sx, double sy, double sp) { x = sx; y = sy; speed = sp; }

	void draw() const override {
		glLineWidth(5);
		glBegin(GL_LINES);
		glColor3f(0.8, 0.8, 0.8); glVertex3f(x, y, 0);
		glColor3f(0.08, 0.08, 0.13); glVertex3f(x + 8, y, 0); // +8 для их растягивания вдоль x
		glEnd();

	}

};

class Bullet : public Entity {
public:

	Bullet(double bx, double by, double sp) { x = bx; y = by; speed = sp; }

	void draw() const override {
		glLineWidth(5);
		glBegin(GL_LINES);
		glColor3f(1, 0.4, 0); glVertex3f(x, y, 0);
		glColor3f(1, 1, 0); glVertex3f(x - 6, y, 0);
		glEnd();

	}
};

class Asteroid : public Entity {
public:

	Asteroid(double ax, double ay, double sp) { x = ax; y = ay; speed = sp; }

	void draw() const override {
		glBegin(GL_POLYGON);
		glColor3f(0.5, 0.5, 0.5); glVertex3f(x - size_first_asteroid, y + size_first_asteroid / 2, 1);
		glColor3f(0.5, 0.5, 0.5); glVertex3f(x - size_first_asteroid, y - size_first_asteroid / 2, 1);
		glColor3f(0.5, 0.5, 0.5); glVertex3f(x - size_first_asteroid / 2, y - size_first_asteroid, 1);
		glColor3f(0.7, 0.7, 0.7); glVertex3f(x + size_first_asteroid / 2, y - size_first_asteroid, 1);
		glColor3f(0.7, 0.7, 0.7); glVertex3f(x + size_first_asteroid, y - size_first_asteroid / 2, 1);
		glColor3f(0.7, 0.7, 0.7); glVertex3f(x + size_first_asteroid, y + size_first_asteroid / 2, 1);
		glColor3f(0.5, 0.5, 0.5); glVertex3f(x + size_first_asteroid / 2, y + size_first_asteroid, 1);
		glColor3f(0.5, 0.5, 0.5); glVertex3f(x - size_first_asteroid / 2, y + size_first_asteroid, 1);
		glEnd();

		glPointSize(size_first_asteroid * 5 / 7);
		glBegin(GL_POINTS);
		glColor3f(0.4, 0.4, 0.4); glVertex3f(x - size_first_asteroid / 2, y - size_first_asteroid / 4, 0);
		glColor3f(0.35, 0.35, 0.35); glVertex3f(x - size_first_asteroid / 4, y - size_first_asteroid / 2, 0);
		glColor3f(0.35, 0.35, 0.35); glVertex3f(x - size_first_asteroid / 3, y + size_first_asteroid / 2, 0);
		glColor3f(0.55, 0.55, 0.55); glVertex3f(x + size_first_asteroid / 1.9, y + size_first_asteroid / 3, 0);
		glEnd();

	}
};

class Bonus : public Entity {
public:

	// 1 - жизни, 2 - бонус х2
	int type;

	Bonus(double bx, double by, double sp, int t) { x = bx; y = by; speed = sp; type = t; }

	void draw() const override {
		// жизни
		if (type == 1) {
			glBegin(GL_POLYGON);
			glColor3f(1, 0, 0); glVertex3f(x, y - 7 * size_of_bonus, 0);
			glColor3f(1, 0, 0); glVertex3f(x + 3 * size_of_bonus, y - 9 * size_of_bonus, 0);
			glColor3f(1, 0, 0); glVertex3f(x + 6 * size_of_bonus, y - 9 * size_of_bonus, 0);
			glColor3f(1, 0, 0); glVertex3f(x + 9 * size_of_bonus, y - 6 * size_of_bonus, 0);
			glColor3f(1, 0, 0); glVertex3f(x + 9 * size_of_bonus, y - 2 * size_of_bonus, 0);
			glColor3f(1, 0, 0); glVertex3f(x + 6 * size_of_bonus, y + 3 * size_of_bonus, 0);
			glColor3f(1, 0, 0); glVertex3f(x, y + 9 * size_of_bonus, 0);
			glColor3f(1, 0, 0); glVertex3f(x - 6 * size_of_bonus, y + 3 * size_of_bonus, 0);
			glColor3f(1, 0, 0); glVertex3f(x - 9 * size_of_bonus, y - 2 * size_of_bonus, 0);
			glColor3f(1, 0, 0); glVertex3f(x - 9 * size_of_bonus, y - 6 * size_of_bonus, 0);
			glColor3f(1, 0, 0); glVertex3f(x - 6 * size_of_bonus, y - 9 * size_of_bonus, 0);
			glColor3f(1, 0, 0); glVertex3f(x - 3 * size_of_bonus, y - 9 * size_of_bonus, 0);
			glColor3f(1, 0, 0); glVertex3f(x - 0 * size_of_bonus, y - 7 * size_of_bonus, 0);
			glEnd();

			glLineWidth(size_of_bonus * 4);
			glBegin(GL_LINES);
			glColor3f(1, 1, 0); glVertex3f(x - 13 * size_of_bonus, y + 12 * size_of_bonus, 0);
			glColor3f(1, 1, 0); glVertex3f(x - 13 * size_of_bonus, y - 12 * size_of_bonus, 0);

			glColor3f(1, 1, 0); glVertex3f(x - 12 * size_of_bonus, y - 13 * size_of_bonus, 0);
			glColor3f(1, 1, 0); glVertex3f(x + 12 * size_of_bonus, y - 13 * size_of_bonus, 0);

			glColor3f(1, 1, 0); glVertex3f(x + 13 * size_of_bonus, y - 12 * size_of_bonus, 0);
			glColor3f(1, 1, 0); glVertex3f(x + 13 * size_of_bonus, y + 12 * size_of_bonus, 0);

			glColor3f(1, 1, 0); glVertex3f(x + 12 * size_of_bonus, y + 13 * size_of_bonus, 0);
			glColor3f(1, 1, 0); glVertex3f(x - 12 * size_of_bonus, y + 13 * size_of_bonus, 0);
			glEnd();

		}

		//доп очки
		else if (type == 2) {
			glLineWidth(size_of_bonus * 8);
			glBegin(GL_LINES);
			glColor3f(1, 0, 0); glVertex3f(x - 9 * size_of_bonus, y - 9 * size_of_bonus, 0); // X начало
			glColor3f(1, 0, 0); glVertex3f(x - 3 * size_of_bonus, y + 9 * size_of_bonus, 0);

			glColor3f(1, 0, 0); glVertex3f(x - 3 * size_of_bonus, y - 9 * size_of_bonus, 0);
			glColor3f(1, 0, 0); glVertex3f(x - 9 * size_of_bonus, y + 9 * size_of_bonus, 0); // Х конец

			glColor3f(1, 0, 0); glVertex3f(x + 1 * size_of_bonus, y - 8 * size_of_bonus, 0);
			glColor3f(1, 0, 0); glVertex3f(x + 8 * size_of_bonus, y - 8 * size_of_bonus, 0);

			glColor3f(1, 0, 0); glVertex3f(x + 8 * size_of_bonus, y - 8 * size_of_bonus, 0);
			glColor3f(1, 0, 0); glVertex3f(x - 0 * size_of_bonus, y + 8 * size_of_bonus, 0);

			glColor3f(1, 0, 0); glVertex3f(x - 0 * size_of_bonus, y + 8 * size_of_bonus, 0);
			glColor3f(1, 0, 0); glVertex3f(x + 8 * size_of_bonus, y + 8 * size_of_bonus, 0);

			glEnd();


			glLineWidth(size_of_bonus * 4);
			glBegin(GL_LINES);
			glColor3f(1, 1, 0); glVertex3f(x - 13 * size_of_bonus, y + 12 * size_of_bonus, 0);
			glColor3f(1, 1, 0); glVertex3f(x - 13 * size_of_bonus, y - 12 * size_of_bonus, 0);

			glColor3f(1, 1, 0); glVertex3f(x - 12 * size_of_bonus, y - 13 * size_of_bonus, 0);
			glColor3f(1, 1, 0); glVertex3f(x + 12 * size_of_bonus, y - 13 * size_of_bonus, 0);

			glColor3f(1, 1, 0); glVertex3f(x + 13 * size_of_bonus, y - 12 * size_of_bonus, 0);
			glColor3f(1, 1, 0); glVertex3f(x + 13 * size_of_bonus, y + 12 * size_of_bonus, 0);

			glColor3f(1, 1, 0); glVertex3f(x + 12 * size_of_bonus, y + 13 * size_of_bonus, 0);
			glColor3f(1, 1, 0); glVertex3f(x - 12 * size_of_bonus, y + 13 * size_of_bonus, 0);
			glEnd();

		}
	}

};

class Spaceship : public Entity {
public:

	double step = 10; //шаг перемещения


	Spaceship() { x = -65; y = 0; }

	void draw() const override {
		// ОГОНЬ
		glPointSize(size_of_spaceship * 0.5);
		glBegin(GL_POINTS);
		glColor3f(1, 1, 0); glVertex3f(x - 2.7 * size_of_spaceship - (rand() % 3), y - size_of_spaceship + 1 + (rand() % 13), 0);
		glColor3f(1, 1, 0); glVertex3f(x - 2.7 * size_of_spaceship - (rand() % 3), y - size_of_spaceship + 1 + (rand() % 13), 0);
		glColor3f(1, 1, 0); glVertex3f(x - 2.7 * size_of_spaceship - (rand() % 3), y - size_of_spaceship + 1 + (rand() % 13), 0);
		glColor3f(1, 1, 0); glVertex3f(x - 2.7 * size_of_spaceship - (rand() % 3), y - size_of_spaceship + 1 + (rand() % 13), 0);

		glColor3f(1, 0, 0); glVertex3f(x - 2.7 * size_of_spaceship - (rand() % 3), y - size_of_spaceship + 1 + (rand() % 13), 0);
		glColor3f(1, 0, 0); glVertex3f(x - 2.7 * size_of_spaceship - (rand() % 3), y - size_of_spaceship + 1 + (rand() % 13), 0);
		glColor3f(1, 0, 0); glVertex3f(x - 2.7 * size_of_spaceship - (rand() % 3), y - size_of_spaceship + 1 + (rand() % 13), 0);
		glColor3f(1, 0, 0); glVertex3f(x - 2.7 * size_of_spaceship - (rand() % 3), y - size_of_spaceship + 1 + (rand() % 13), 0);
		glEnd();

		// КОРАБЛЬ
		glBegin(GL_POLYGON);
		glColor3f(0.5, 0.5, 0.9); glVertex3f(x, y, 0);
		glColor3f(1, 1, 1); glVertex3f(x - size_of_spaceship, y + size_of_spaceship, 0);
		glColor3f(1, 1, 1); glVertex3f(x - size_of_spaceship * 2.5, y + 0 * size_of_spaceship, 0);
		glColor3f(1, 1, 1); glVertex3f(x - size_of_spaceship, y - size_of_spaceship, 0);
		glEnd();

		glBegin(GL_POLYGON);
		glColor3f(1, 1, 1); glVertex3f(x - 2 * size_of_spaceship, y, 0);
		glColor3f(1, 1, 1); glVertex3f(x - 2.7 * size_of_spaceship, y - size_of_spaceship, 0);
		glColor3f(1, 1, 1); glVertex3f(x - 2.7 * size_of_spaceship, y + size_of_spaceship, 0);
		glEnd();

		glLineWidth(size_of_spaceship * 0.3);
		glBegin(GL_LINES);
		glColor3f(1, 1, 1); glVertex3f(x - 2.7 * size_of_spaceship, y - size_of_spaceship, 0);
		glColor3f(1, 1, 1); glVertex3f(x - 3 * size_of_spaceship, y - size_of_spaceship, 0);

		glColor3f(1, 1, 1); glVertex3f(x - 2.7 * size_of_spaceship, y + size_of_spaceship, 0);
		glColor3f(1, 1, 1); glVertex3f(x - 3 * size_of_spaceship, y + size_of_spaceship, 0);
		glEnd();
		
	}

	void move(unsigned char key) {

		if ((key == 'w') || (key == 'W') || (key == '8')) {
			if (y > -70) y -= step;  // -= т.к. перевернута система координат (а это нужно для надписей)
		}
		if ((key == 's') || (key == 'S') || (key == '2')) {
			if (y < 90) y += step;
		}
		if (((key == 'd') || (key == 'D') || (key == '6')) && (x < 95)) x += step;
		if (((key == 'a') || (key == 'A') || (key == '4')) && (x > -75)) x -= step;
		
	}
};


// GAME PROCESS FUNCTIONS
class Game_manager {
public:
	
	// пули корабля
	std::vector<std::unique_ptr<Bullet>> bullets;

	// звезды - фон
	std::vector<std::unique_ptr<Star>> stars;

	// астероиды - то, что уничтожаем
	std::vector<std::unique_ptr<Asteroid>> asteroids;

	// бонусы
	std::vector<std::unique_ptr<Bonus>> bonuses;

	// Корабль
	Spaceship spaceship;

	// текущие игровые значения
	int posibility_of_spawn_bonus = 100;
	int posibility_of_spawn_asteroids = 30; // меняется в keyboard
	double time_x2_bonus = 0; // время действия x2 бонуса
	time_t last_lost_life = -REGENIGATION_TIME; // чтоб не моргал в начале // нужно, чтоб проходило какое-то время после потери жизни. эта переменная будет отсчитывать это время
	time_t last_taken_bonus; // нужно, чтоб проходило какое-то время после потери жизни. эта переменная будет отсчитывать это время
	int choose = 1; //нужно для выбора в меню. 1 - подсвечивает easy, 2 - medium, 3 - hard 
	int score = 0; // очки
	int lives = 3;
	time_t last_shooted_bullet = clock();; // время (будет создаваться как clock()) последней выстреленной пули
	// нужно, чтобы сделать так, чтоб пули не летели одним потоком (ограничить количество пуль в ед. времени)

	void draw_bonuses() {
		if ((rand() % posibility_of_spawn_bonus) == 9) {   //выбираем случайное время, при достижении которого генерируется звезда. чем больше значение после %, тем ниже вероятность появления
			double y = ((rand() % 18) * 10) - 75; //выбирается случайное значение высоты для появившейся звезды. 75 (вместо 90) - немного сдвигаем вниз, чтоб не залезали на интерфейс
			int type = rand() % 3;
			bonuses.push_back(std::make_unique<Bonus>(100, y, speed_of_bonus, type));
		}

		for (int i = 0; i < bonuses.size(); i++) {
			if (bonuses[i]->alive == false) {
				bonuses.erase(bonuses.begin() + i);
				i--; // чтобы не пропустить следующий
			}
		}

		for (auto& b : bonuses) {
			b->update();
			b->draw();
		}

	}

	void draw_asteroids() {
		if ((rand() % posibility_of_spawn_asteroids) == 9) {   //выбираем случайное время, при достижении которого генерируется астероид
			double y = ((rand() % 16) * 10) - 70; //выбирается случайное значение высоты для появившегося астероида. 70 и 16 (вместо 90 и 18) - немного сдвигаем вниз, чтоб не залезали на интерфейс
			double speed = (speed_of_asteroids * (rand() % 10)) / 10 + 0.1; // скорость. добавляем константу, чтоб те астероиды, у которых скорость выпала 0 тоже двигались.
			asteroids.push_back(std::make_unique<Asteroid>(100, y, speed));
		}

		for (int i = 0; i < asteroids.size(); i++) {
			if (asteroids[i]->alive == false) {
				asteroids.erase(asteroids.begin() + i);
				i--; // чтобы не пропустить следующий
			}
		}

		for (auto& a : asteroids) {
			a->update();
			a->draw();
		}
	}

	void draw_stars() { //ф-я которая создаёт звезды на фоне.
		if ((rand() % 10) == 9) {   //выбираем случайное время, при достижении которого генерируется звезда. чем больше значение после %, тем ниже вероятность появления
			double y = ((rand() % 18) * 10) - 75; //выбирается случайное значение высоты для появившейся звезды. 75 (вместо 90) - немного сдвигаем вниз, чтоб не залезали на интерфейс
			double speed = (speed_of_stars * (rand() % 10)) / 10 + 0.1; // скорость. добавляем константу, чтоб те звезды, у которых скорость выпала 0 тоже двигались.
			stars.push_back(std::make_unique<Star>(100, y, speed));
		}

		for (auto& s : stars) s->update();
		for (auto& s : stars) s->draw();
	}

	void bullet() { // пуля
		for (int i = 0; i < bullets.size(); i++) {
			if (bullets[i]->alive == false) {
				bullets.erase(bullets.begin() + i);
				i--; // чтобы не пропустить следующий
			}
		}
		for (auto& b : bullets) {
			b->update();
			b->draw();
		}
	}

	void draw_spaceship() {

		// если исполняется, кораблик исчезает (начинает моргать)
		if (((clock() - last_lost_life < REGENIGATION_TIME) && (((clock() % 100) / 10) % 2 == 1)));
		// иначе рисуется
		else spaceship.draw();
	}

	void keyboard(unsigned char key, int x, int y) {  //перемещение корабля

		if (key == 13) {
			difficulty = choose; // чем меньше значение, тем больше вероятность
			if (difficulty == 1) posibility_of_spawn_asteroids = 30;
			if (difficulty == 2) posibility_of_spawn_asteroids = 20;
			if (difficulty == 3) {
				posibility_of_spawn_asteroids = 10;
				speed_of_asteroids += 0.5;
			}
		}
		if (key == 27) {
			if (difficulty != -1) difficulty = -2;
		}

		//перемещает черный прямоугольник в меню
		if (difficulty == 0) {
			if ((key == 'w') || (key == 'W') || (key == '8')) {
				if (choose > 1) choose--;
			}
			if ((key == 's') || (key == 'S') || (key == '2')) {
				if (choose < 3) choose++;
			}
		}

		if ((key == ' ') || (key == '5')) {
			if (clock() - last_shooted_bullet > 150) { // проверяем, чтоб прошло какое-то время после последней пули
				last_shooted_bullet = clock();
				bullets.push_back(std::make_unique<Bullet>(spaceship.x, spaceship.y, speed_of_bullet));
			}
		}

		if (difficulty > 0)	spaceship.move(key);
	}

	void menu() {
		char c1[40] = "Choose difficulty:";
		print_string(-48, -40, c1, 1, 1, 1);
		int dist; //перемещает черный прямоугольник в зависимости от выбора
		if (choose > 0) {
			if (choose == 1) dist = 0;
			if (choose == 2) dist = 15;
			if (choose == 3) dist = 30;
			glBegin(GL_POLYGON);
			glColor3f(0.3, 0.3, 0.4); glVertex3f(-50, -26 + dist, 1);
			glColor3f(0.3, 0.3, 0.4); glVertex3f(-50, -16 + dist, 1);
			glColor3f(0.3, 0.3, 0.4); glVertex3f(45, -16 + dist, 1);
			glColor3f(0.3, 0.3, 0.4); glVertex3f(45, -26 + dist, 1);
			glEnd();
		}

		char c2[10] = "- Easy";
		char c3[10] = "- Medium";
		char c4[10] = "- Hard";
		print_string(-48, -25, c2, 0, 1, 0);
		print_string(-48, -10, c3, 1, 1, 0);
		print_string(-48, 5, c4, 1, 0, 0);
	}

	void interface() {
		char str_score[9];
		int copy_score = score; // копия очков, с которой можно проводить разные операции
		for (int i = 0; i < 8; i++) {
			str_score[8 - i - 1] = copy_score % 10 + '0';
			copy_score = copy_score / 10;
		}
		str_score[8] = '\0';
		print_string(50, -90, str_score, 1, 1, 1);

		double heart_size = 0.6;
		if (lives >= 1) {
			int xHeart1 = 00;
			int yHeart1 = -88;
			glBegin(GL_POLYGON);
			glColor3f(1, 0, 0); glVertex3f(xHeart1, yHeart1 - 7 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart1 + 3 * heart_size, yHeart1 - 9 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart1 + 6 * heart_size, yHeart1 - 9 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart1 + 9 * heart_size, yHeart1 - 6 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart1 + 9 * heart_size, yHeart1 - 2 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart1 + 6 * heart_size, yHeart1 + 3 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart1, yHeart1 + 9 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart1 - 6 * heart_size, yHeart1 + 3 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart1 - 9 * heart_size, yHeart1 - 2 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart1 - 9 * heart_size, yHeart1 - 6 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart1 - 6 * heart_size, yHeart1 - 9 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart1 - 3 * heart_size, yHeart1 - 9 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart1 - 0 * heart_size, yHeart1 - 7 * heart_size, 0);
			glEnd();
		}
		if (lives >= 2) {
			int xHeart2 = 15;
			int yHeart2 = -88;
			glBegin(GL_POLYGON);
			glColor3f(1, 0, 0); glVertex3f(xHeart2, yHeart2 - 7 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart2 + 3 * heart_size, yHeart2 - 9 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart2 + 6 * heart_size, yHeart2 - 9 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart2 + 9 * heart_size, yHeart2 - 6 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart2 + 9 * heart_size, yHeart2 - 2 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart2 + 6 * heart_size, yHeart2 + 3 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart2, yHeart2 + 9 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart2 - 6 * heart_size, yHeart2 + 3 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart2 - 9 * heart_size, yHeart2 - 2 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart2 - 9 * heart_size, yHeart2 - 6 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart2 - 6 * heart_size, yHeart2 - 9 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart2 - 3 * heart_size, yHeart2 - 9 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart2 - 0 * heart_size, yHeart2 - 7 * heart_size, 0);
			glEnd();
		}
		if (lives >= 3) {
			int xHeart3 = 30;
			int yHeart3 = -88;
			glBegin(GL_POLYGON);
			glColor3f(1, 0, 0); glVertex3f(xHeart3, yHeart3 - 7 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart3 + 3 * heart_size, yHeart3 - 9 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart3 + 6 * heart_size, yHeart3 - 9 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart3 + 9 * heart_size, yHeart3 - 6 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart3 + 9 * heart_size, yHeart3 - 2 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart3 + 6 * heart_size, yHeart3 + 3 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart3, yHeart3 + 9 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart3 - 6 * heart_size, yHeart3 + 3 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart3 - 9 * heart_size, yHeart3 - 2 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart3 - 9 * heart_size, yHeart3 - 6 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart3 - 6 * heart_size, yHeart3 - 9 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart3 - 3 * heart_size, yHeart3 - 9 * heart_size, 0);
			glColor3f(1, 0, 0); glVertex3f(xHeart3 - 0 * heart_size, yHeart3 - 7 * heart_size, 0);
			glEnd();
		}

		if (time_x2_bonus > 0) {
			double xPos = -70;
			double yPos = -90;
			double size = 0.4;
			time_x2_bonus -= 5;

			glLineWidth(size * 32);
			glBegin(GL_LINES);
			glColor3f(1, 1, 0); glVertex3f(xPos + 20 * size, yPos + 0 * size, 0);
			glColor3f(1, 1, 0); glVertex3f(xPos + 20 * size + 0.01 * time_x2_bonus, yPos + 0 * size, 0);
			glEnd();

			glLineWidth(size * 8);
			glBegin(GL_LINES);
			glColor3f(1, 0, 0); glVertex3f(xPos - 9 * size, yPos - 9 * size, 0); // X начало
			glColor3f(1, 0, 0); glVertex3f(xPos - 3 * size, yPos + 9 * size, 0);

			glColor3f(1, 0, 0); glVertex3f(xPos - 3 * size, yPos - 9 * size, 0);
			glColor3f(1, 0, 0); glVertex3f(xPos - 9 * size, yPos + 9 * size, 0); // Х конец

			glColor3f(1, 0, 0); glVertex3f(xPos + 1 * size, yPos - 8 * size, 0);
			glColor3f(1, 0, 0); glVertex3f(xPos + 8 * size, yPos - 8 * size, 0);

			glColor3f(1, 0, 0); glVertex3f(xPos + 8 * size, yPos - 8 * size, 0);
			glColor3f(1, 0, 0); glVertex3f(xPos - 0 * size, yPos + 8 * size, 0);

			glColor3f(1, 0, 0); glVertex3f(xPos - 0 * size, yPos + 8 * size, 0);
			glColor3f(1, 0, 0); glVertex3f(xPos + 8 * size, yPos + 8 * size, 0);
			glEnd();

			glLineWidth(size * 4);
			glBegin(GL_LINES);
			glColor3f(1, 1, 0); glVertex3f(xPos - 13 * size, yPos + 12 * size, 0);
			glColor3f(1, 1, 0); glVertex3f(xPos - 13 * size, yPos - 12 * size, 0);

			glColor3f(1, 1, 0); glVertex3f(xPos - 12 * size, yPos - 13 * size, 0);
			glColor3f(1, 1, 0); glVertex3f(xPos + 12 * size, yPos - 13 * size, 0);

			glColor3f(1, 1, 0); glVertex3f(xPos + 13 * size, yPos - 12 * size, 0);
			glColor3f(1, 1, 0); glVertex3f(xPos + 13 * size, yPos + 12 * size, 0);

			glColor3f(1, 1, 0); glVertex3f(xPos + 12 * size, yPos + 13 * size, 0);
			glColor3f(1, 1, 0); glVertex3f(xPos - 12 * size, yPos + 13 * size, 0);
			glEnd();


		}
	}

	void pause() {
		print_string(-75, -30, "          PAUSE\n (press enter to continue)", 1, 1, 1);
	}

	void game_end_screen() {
		print_string(-30, -30, "GAME OVER", 1, 0, 0);
	}

	void check_hitted_asteroid() { // проверяет попала ли пуля в астероид. если да - отправляет его за карту

		for (auto& a : asteroids) {
			for (auto& b : bullets) {
				if ((a->y - size_first_asteroid <= b->y) && (a->y + size_first_asteroid >= b->y)) { //если пуля попала в диапазон ширины астероида
					if ((a->x - size_first_asteroid <= b->x) && (a->x >= b->x)) { // и их координаты по х примерно равны
						// помечаем как неживых. Далее при проверке они пропадут
						b->alive = false;
						a->alive = false;
						score++;
						if (time_x2_bonus > 0) score++;
					}
				}

			}
		}
	}

	void check_hitted_spaceship() {
		for (auto& a : asteroids) {
			if ((a->y - size_first_asteroid - size_of_spaceship <= spaceship.y) &&
				(a->y + size_first_asteroid + size_of_spaceship >= spaceship.y)) {
				if ((a->x - size_of_spaceship <= spaceship.x) && (a->x + size_of_spaceship * 4 >= spaceship.x)) {
					if (clock() - last_lost_life > REGENIGATION_TIME) { // 2500 тиков - время форы перед новым снятием сердца
						lives--;
						last_lost_life = clock();
						if (lives == 0) {
							difficulty = -1; // если жизни кончились - проигрываем :)
							choose = 0; // не 1 чтоб нельзя было возродится нажав enter
							score = 0;
							lives = 3;

							// очищаем всё кроме звезд (они не мешают)
							bonuses.clear();
							asteroids.clear();
							bullets.clear();
							spaceship.x = -65;
							spaceship.y = 0;
						}
					}
				}
			}
		}
	}

	void check_given_bonus() {
		for (auto& b : bonuses) {
			if ((b->y - size_of_bonus - size_of_spaceship <= spaceship.y) &&
				(b->y + size_of_bonus + size_of_spaceship >= spaceship.y)) {
				if ((b->x - size_of_spaceship <= spaceship.x) && (b->x + size_of_spaceship * 4 >= spaceship.x)) {
					if (clock() - last_taken_bonus > CAN_TAKE_NEW_BONUS) {
						if (b->type == 1) { // доп жизни
							if (lives < 3) lives++;
							last_taken_bonus = clock();
							b->alive = false;
						}
						if (b->type == 2) { // мультипликатор очков
							time_x2_bonus = 4000;  // время действия бонуса
							last_taken_bonus = clock();
							b->alive = false;
						}
					}
				}
			}
		}
	}

};

Game_manager game;



void keyboard_wrapper(unsigned char key, int x, int y) {
	game.keyboard(key, x, y);
}

void display() {
	glClear(GL_COLOR_BUFFER_BIT);
	if (difficulty > 0) { // на переднем плане рисуется то, что здесь стоит последним
		game.draw_stars();
		game.bullet();
		game.draw_asteroids();
		game.draw_bonuses();

		game.draw_spaceship();

		game.check_given_bonus();
		game.check_hitted_spaceship();
		game.check_hitted_asteroid();

		game.interface();
	}
	else if (difficulty == 0) game.menu();
	else if (difficulty == -1) { // 4 - проиграл
		game.game_end_screen();
	}
	else if (difficulty = -2) {
		game.pause();
	}

	glutSwapBuffers();
}

void time_my(int num) {
	glutPostRedisplay();
	glutTimerFunc(16, time_my, 0);
}

int main(int argc, char** argv) {

	srand(time(NULL));

	glutInit(&argc, argv);
	glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB);
	glutInitWindowPosition(80, 80);
	glutInitWindowSize(600, 400);
	glutCreateWindow("Space Impact");
	glClearColor(0.08, 0.08, 0.13, 1);

	if (difficulty == 0) glScalef(0.01, -0.01, 0.1); // scaling text at the beginnings
	glutDisplayFunc(display);
	glutKeyboardFunc(keyboard_wrapper);
	glutTimerFunc(0, time_my, 0);

	glutMainLoop();
}

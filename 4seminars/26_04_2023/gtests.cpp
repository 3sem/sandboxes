// Google Tests fixture example -- try it with
// ./gtests --gtest_filter=*test1
// ./gtests --gtest_list_tests
// ./gtests

#include <gtest/gtest.h>

class A {
public:
        A():i(0) {
                  std::cout << "I am constructor\n";
          }
        ~A() {
                std::cout << " I am destrutor\n";
        }
        int i;
};

class TWrapper:public testing::Test {
        protected:
                void SetUp() {
                        a = new A;
                        a ->i = 5;
                }

                void TearDown() {
                        delete a;
                }
                A *a;
};

TEST_F(TWrapper, test1) {
        ASSERT_EQ(a->i, 5);
        a->i++;
}

TEST_F(TWrapper, test2) {
        ASSERT_EQ(a->i, 5);
}

int main(int argc, char **argv) {
        ::testing::InitGoogleTest(&argc, argv);
        //::testing::GTEST_FLAG(filter) = "TWrapper";
        RUN_ALL_TESTS();
        return 0;
}
